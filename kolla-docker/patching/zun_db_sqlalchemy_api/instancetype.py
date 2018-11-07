    # instancetype section
    def _add_instancetypes_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_instancetypes(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Instancetype)
        # query = self._add_tenant_filters(context, query)
        query = self._add_instancetypes_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_instancetypes xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of instancetypes is %s', (sort_key))
        return _paginate_query(models.Instancetype, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_instancetype_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Instancetype). \
            filter(func.lower(models.Instancetype.name) == lowername)
        instancetype_with_same_name = base_query.count()
        if instancetype_with_same_name > 0:
            raise exception.InstancetypeAlreadyExists(field='name',
                                                  value=lowername)

    def create_instancetype(self, context, values):
        # ensure defaults are present for new instancetypes
        LOG.debug('sqlalchemy api.py create_instancetype xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_instancetype_name(context, values['name'])

        instancetype = models.Instancetype()
        instancetype.update(values)
        try:
            instancetype.save()
        except db_exc.DBDuplicateEntry:
            raise exception.InstancetypeAlreadyExists(field='name',
                                                  value=values['name'])
        return instancetype

    def get_instancetype_by_uuid(self, context, instancetype_uuid):
        query = model_query(models.Instancetype)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=instancetype_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.InstancetypeNotFound(instancetype=instancetype_uuid)

    def get_instancetype_by_name(self, context, instancetype_name):
        query = model_query(models.Instancetype)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=instancetype_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.InstancetypeNotFound(instancetype=instancetype_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple instancetypes exist with same '
                                     'name. Please use the instancetype uuid '
                                     'instead.')

    def destroy_instancetype(self, context, instancetype_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Instancetype, session=session)
            query = add_identity_filter(query, instancetype_id)
            count = query.delete()
            if count != 1:
                raise exception.InstancetypeNotFound(instancetype_id)

    def update_instancetype(self, context, instancetype_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Instancetype.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_instancetype_name(context, values['name'])

        return self._do_update_instancetype(instancetype_id, values)

    def _do_update_instancetype(self, instancetype_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Instancetype, session=session)
            query = add_identity_filter(query, instancetype_id)
            LOG.debug('_do_update_instancetype xxxxxx instancetype_id =%s, query=%s, values=%s',
                      instancetype_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.InstancetypeNotFound(instancetype=instancetype_id)

            ref.update(values)
        return ref
