    # storagerate section
    def _add_storagerates_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_storagerates(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Storagerate)
        # query = self._add_tenant_filters(context, query)
        query = self._add_storagerates_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_storagerates xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of storagerates is %s', (sort_key))
        return _paginate_query(models.Storagerate, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_storagerate_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Storagerate). \
            filter(func.lower(models.Storagerate.name) == lowername)
        storagerate_with_same_name = base_query.count()
        if storagerate_with_same_name > 0:
            raise exception.StoragerateAlreadyExists(field='name',
                                                  value=lowername)

    def create_storagerate(self, context, values):
        # ensure defaults are present for new storagerates
        LOG.debug('sqlalchemy api.py create_storagerate xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_storagerate_name(context, values['name'])

        storagerate = models.Storagerate()
        storagerate.update(values)
        try:
            storagerate.save()
        except db_exc.DBDuplicateEntry:
            raise exception.StoragerateAlreadyExists(field='name',
                                                  value=values['name'])
        return storagerate

    def get_storagerate_by_uuid(self, context, storagerate_uuid):
        query = model_query(models.Storagerate)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=storagerate_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.StoragerateNotFound(storagerate=storagerate_uuid)

    def get_storagerate_by_name(self, context, storagerate_name):
        query = model_query(models.Storagerate)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=storagerate_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.StoragerateNotFound(storagerate=storagerate_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple storagerates exist with same '
                                     'name. Please use the storagerate uuid '
                                     'instead.')

    def destroy_storagerate(self, context, storagerate_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Storagerate, session=session)
            query = add_identity_filter(query, storagerate_id)
            count = query.delete()
            if count != 1:
                raise exception.StoragerateNotFound(storagerate_id)

    def update_storagerate(self, context, storagerate_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Storagerate.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_storagerate_name(context, values['name'])

        return self._do_update_storagerate(storagerate_id, values)

    def _do_update_storagerate(self, storagerate_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Storagerate, session=session)
            query = add_identity_filter(query, storagerate_id)
            LOG.debug('_do_update_storagerate xxxxxx storagerate_id =%s, query=%s, values=%s',
                      storagerate_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.StoragerateNotFound(storagerate=storagerate_id)

            ref.update(values)
        return ref
