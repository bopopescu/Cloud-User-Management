    # providerregion section
    def _add_providerregions_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_providerregions(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Providerregion)
        # query = self._add_tenant_filters(context, query)
        query = self._add_providerregions_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_providerregions xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of providerregions is %s', (sort_key))
        return _paginate_query(models.Providerregion, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_providerregion_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Providerregion). \
            filter(func.lower(models.Providerregion.name) == lowername)
        providerregion_with_same_name = base_query.count()
        if providerregion_with_same_name > 0:
            raise exception.ProviderregionAlreadyExists(field='name',
                                                  value=lowername)

    def create_providerregion(self, context, values):
        # ensure defaults are present for new providerregions
        LOG.debug('sqlalchemy api.py create_providerregion xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_providerregion_name(context, values['name'])

        providerregion = models.Providerregion()
        providerregion.update(values)
        try:
            providerregion.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ProviderregionAlreadyExists(field='name',
                                                  value=values['name'])
        return providerregion

    def get_providerregion_by_uuid(self, context, providerregion_uuid):
        query = model_query(models.Providerregion)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=providerregion_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ProviderregionNotFound(providerregion=providerregion_uuid)

    def get_providerregion_by_name(self, context, providerregion_name):
        query = model_query(models.Providerregion)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=providerregion_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ProviderregionNotFound(providerregion=providerregion_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple providerregions exist with same '
                                     'name. Please use the providerregion uuid '
                                     'instead.')

    def destroy_providerregion(self, context, providerregion_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Providerregion, session=session)
            query = add_identity_filter(query, providerregion_id)
            count = query.delete()
            if count != 1:
                raise exception.ProviderregionNotFound(providerregion_id)

    def update_providerregion(self, context, providerregion_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Providerregion.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_providerregion_name(context, values['name'])

        return self._do_update_providerregion(providerregion_id, values)

    def _do_update_providerregion(self, providerregion_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Providerregion, session=session)
            query = add_identity_filter(query, providerregion_id)
            LOG.debug('_do_update_providerregion xxxxxx providerregion_id =%s, query=%s, values=%s',
                      providerregion_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.ProviderregionNotFound(providerregion=providerregion_id)

            ref.update(values)
        return ref
