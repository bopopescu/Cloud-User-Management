    # provideraccount section
    def _add_provideraccounts_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_provideraccounts(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Provideraccount)
        # query = self._add_tenant_filters(context, query)
        query = self._add_provideraccounts_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_provideraccounts xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of provideraccounts is %s', (sort_key))
        return _paginate_query(models.Provideraccount, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_provideraccount_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Provideraccount). \
            filter(func.lower(models.Provideraccount.name) == lowername)
        provideraccount_with_same_name = base_query.count()
        if provideraccount_with_same_name > 0:
            raise exception.ProvideraccountAlreadyExists(field='name',
                                                  value=lowername)

    def create_provideraccount(self, context, values):
        # ensure defaults are present for new provideraccounts
        LOG.debug('sqlalchemy api.py create_provideraccount xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_provideraccount_name(context, values['name'])

        provideraccount = models.Provideraccount()
        provideraccount.update(values)
        try:
            provideraccount.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ProvideraccountAlreadyExists(field='name',
                                                  value=values['name'])
        return provideraccount

    def get_provideraccount_by_uuid(self, context, provideraccount_uuid):
        query = model_query(models.Provideraccount)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=provideraccount_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ProvideraccountNotFound(provideraccount=provideraccount_uuid)

    def get_provideraccount_by_name(self, context, provideraccount_name):
        query = model_query(models.Provideraccount)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=provideraccount_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ProvideraccountNotFound(provideraccount=provideraccount_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple provideraccounts exist with same '
                                     'name. Please use the provideraccount uuid '
                                     'instead.')

    def destroy_provideraccount(self, context, provideraccount_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Provideraccount, session=session)
            query = add_identity_filter(query, provideraccount_id)
            count = query.delete()
            if count != 1:
                raise exception.ProvideraccountNotFound(provideraccount_id)

    def update_provideraccount(self, context, provideraccount_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Provideraccount.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_provideraccount_name(context, values['name'])

        return self._do_update_provideraccount(provideraccount_id, values)

    def _do_update_provideraccount(self, provideraccount_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Provideraccount, session=session)
            query = add_identity_filter(query, provideraccount_id)
            LOG.debug('_do_update_provideraccount xxxxxx provideraccount_id =%s, query=%s, values=%s',
                      provideraccount_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.ProvideraccountNotFound(provideraccount=provideraccount_id)

            ref.update(values)
        return ref
