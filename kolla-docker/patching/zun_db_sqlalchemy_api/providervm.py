    # providervm section
    def _add_providervms_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_providervms(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Providervm)
        # query = self._add_tenant_filters(context, query)
        query = self._add_providervms_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_providervms xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of providervms is %s', (sort_key))
        return _paginate_query(models.Providervm, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_providervm_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Providervm). \
            filter(func.lower(models.Providervm.name) == lowername)
        providervm_with_same_name = base_query.count()
        if providervm_with_same_name > 0:
            raise exception.ProvidervmAlreadyExists(field='name',
                                                  value=lowername)

    def create_providervm(self, context, values):
        # ensure defaults are present for new providervms
        LOG.debug('sqlalchemy api.py create_providervm xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_providervm_name(context, values['name'])

        providervm = models.Providervm()
        providervm.update(values)
        try:
            providervm.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ProvidervmAlreadyExists(field='name',
                                                  value=values['name'])
        return providervm

    def get_providervm_by_uuid(self, context, providervm_uuid):
        query = model_query(models.Providervm)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=providervm_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ProvidervmNotFound(providervm=providervm_uuid)

    def get_providervm_by_name(self, context, providervm_name):
        query = model_query(models.Providervm)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=providervm_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ProvidervmNotFound(providervm=providervm_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple providervms exist with same '
                                     'name. Please use the providervm uuid '
                                     'instead.')

    def destroy_providervm(self, context, providervm_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Providervm, session=session)
            query = add_identity_filter(query, providervm_id)
            count = query.delete()
            if count != 1:
                raise exception.ProvidervmNotFound(providervm_id)

    def update_providervm(self, context, providervm_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Providervm.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_providervm_name(context, values['name'])

        return self._do_update_providervm(providervm_id, values)

    def _do_update_providervm(self, providervm_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Providervm, session=session)
            query = add_identity_filter(query, providervm_id)
            LOG.debug('_do_update_providervm xxxxxx providervm_id =%s, query=%s, values=%s',
                      providervm_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.ProvidervmNotFound(providervm=providervm_id)

            ref.update(values)
        return ref
