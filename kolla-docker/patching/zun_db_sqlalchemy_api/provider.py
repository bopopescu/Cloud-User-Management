    # provider section
    def _add_providers_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_providers(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Provider)
        # query = self._add_tenant_filters(context, query)
        query = self._add_providers_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_providers xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of providers is %s', (sort_key))
        return _paginate_query(models.Provider, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_provider_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Provider). \
            filter(func.lower(models.Provider.name) == lowername)
        provider_with_same_name = base_query.count()
        if provider_with_same_name > 0:
            raise exception.ProviderAlreadyExists(field='name',
                                                  value=lowername)

    def create_provider(self, context, values):
        # ensure defaults are present for new providers
        LOG.debug('sqlalchemy api.py create_provider xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_provider_name(context, values['name'])

        provider = models.Provider()
        provider.update(values)
        try:
            provider.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ProviderAlreadyExists(field='name',
                                                  value=values['name'])
        return provider

    def get_provider_by_uuid(self, context, provider_uuid):
        query = model_query(models.Provider)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=provider_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ProviderNotFound(provider=provider_uuid)

    def get_provider_by_name(self, context, provider_name):
        query = model_query(models.Provider)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=provider_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ProviderNotFound(provider=provider_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple providers exist with same '
                                     'name. Please use the provider uuid '
                                     'instead.')

    def destroy_provider(self, context, provider_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Provider, session=session)
            query = add_identity_filter(query, provider_id)
            count = query.delete()
            if count != 1:
                raise exception.ProviderNotFound(provider_id)

    def update_provider(self, context, provider_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Provider.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_provider_name(context, values['name'])

        return self._do_update_provider(provider_id, values)

    def _do_update_provider(self, provider_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Provider, session=session)
            query = add_identity_filter(query, provider_id)
            LOG.debug('_do_update_provider xxxxxx provider_id =%s, query=%s, values=%s',
                      provider_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.ProviderNotFound(provider=provider_id)

            ref.update(values)
        return ref
