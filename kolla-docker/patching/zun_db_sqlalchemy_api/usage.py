    # usage section
    def _add_usages_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_usages(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Usage)
        # query = self._add_tenant_filters(context, query)
        query = self._add_usages_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_usages xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of usages is %s', (sort_key))
        return _paginate_query(models.Usage, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_usage_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Usage). \
            filter(func.lower(models.Usage.name) == lowername)
        usage_with_same_name = base_query.count()
        if usage_with_same_name > 0:
            raise exception.UsageAlreadyExists(field='name',
                                                  value=lowername)

    def create_usage(self, context, values):
        # ensure defaults are present for new usages
        LOG.debug('sqlalchemy api.py create_usage xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_usage_name(context, values['name'])

        usage = models.Usage()
        usage.update(values)
        try:
            usage.save()
        except db_exc.DBDuplicateEntry:
            raise exception.UsageAlreadyExists(field='name',
                                                  value=values['name'])
        return usage

    def get_usage_by_uuid(self, context, usage_uuid):
        query = model_query(models.Usage)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=usage_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.UsageNotFound(usage=usage_uuid)

    def get_usage_by_name(self, context, usage_name):
        query = model_query(models.Usage)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=usage_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.UsageNotFound(usage=usage_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple usages exist with same '
                                     'name. Please use the usage uuid '
                                     'instead.')

    def destroy_usage(self, context, usage_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Usage, session=session)
            query = add_identity_filter(query, usage_id)
            count = query.delete()
            if count != 1:
                raise exception.UsageNotFound(usage_id)

    def update_usage(self, context, usage_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Usage.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_usage_name(context, values['name'])

        return self._do_update_usage(usage_id, values)

    def _do_update_usage(self, usage_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Usage, session=session)
            query = add_identity_filter(query, usage_id)
            LOG.debug('_do_update_usage xxxxxx usage_id =%s, query=%s, values=%s',
                      usage_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.UsageNotFound(usage=usage_id)

            ref.update(values)
        return ref
