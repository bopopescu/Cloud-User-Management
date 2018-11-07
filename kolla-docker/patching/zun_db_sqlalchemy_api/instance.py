    # instance section
    def _add_instances_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_instances(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Instance)
        # query = self._add_tenant_filters(context, query)
        query = self._add_instances_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_instances xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of instances is %s', (sort_key))
        return _paginate_query(models.Instance, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_instance_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Instance). \
            filter(func.lower(models.Instance.name) == lowername)
        instance_with_same_name = base_query.count()
        if instance_with_same_name > 0:
            raise exception.InstanceAlreadyExists(field='name',
                                                  value=lowername)

    def create_instance(self, context, values):
        # ensure defaults are present for new instances
        LOG.debug('sqlalchemy api.py create_instance xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_instance_name(context, values['name'])

        instance = models.Instance()
        instance.update(values)
        try:
            instance.save()
        except db_exc.DBDuplicateEntry:
            raise exception.InstanceAlreadyExists(field='name',
                                                  value=values['name'])
        return instance

    def get_instance_by_uuid(self, context, instance_uuid):
        query = model_query(models.Instance)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=instance_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.InstanceNotFound(instance=instance_uuid)

    def get_instance_by_name(self, context, instance_name):
        query = model_query(models.Instance)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=instance_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.InstanceNotFound(instance=instance_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple instances exist with same '
                                     'name. Please use the instance uuid '
                                     'instead.')

    def destroy_instance(self, context, instance_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Instance, session=session)
            query = add_identity_filter(query, instance_id)
            count = query.delete()
            if count != 1:
                raise exception.InstanceNotFound(instance_id)

    def update_instance(self, context, instance_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Instance.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_instance_name(context, values['name'])

        return self._do_update_instance(instance_id, values)

    def _do_update_instance(self, instance_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Instance, session=session)
            query = add_identity_filter(query, instance_id)
            LOG.debug('_do_update_instance xxxxxx instance_id =%s, query=%s, values=%s',
                      instance_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.InstanceNotFound(instance=instance_id)

            ref.update(values)
        return ref
