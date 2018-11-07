    # computerate section
    def _add_computerates_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_computerates(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Computerate)
        # query = self._add_tenant_filters(context, query)
        query = self._add_computerates_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_computerates xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of computerates is %s', (sort_key))
        return _paginate_query(models.Computerate, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_computerate_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Computerate). \
            filter(func.lower(models.Computerate.name) == lowername)
        computerate_with_same_name = base_query.count()
        if computerate_with_same_name > 0:
            raise exception.ComputerateAlreadyExists(field='name',
                                                  value=lowername)

    def create_computerate(self, context, values):
        # ensure defaults are present for new computerates
        LOG.debug('sqlalchemy api.py create_computerate xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_computerate_name(context, values['name'])

        computerate = models.Computerate()
        computerate.update(values)
        try:
            computerate.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ComputerateAlreadyExists(field='name',
                                                  value=values['name'])
        return computerate

    def get_computerate_by_uuid(self, context, computerate_uuid):
        query = model_query(models.Computerate)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=computerate_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ComputerateNotFound(computerate=computerate_uuid)

    def get_computerate_by_name(self, context, computerate_name):
        query = model_query(models.Computerate)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=computerate_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ComputerateNotFound(computerate=computerate_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple computerates exist with same '
                                     'name. Please use the computerate uuid '
                                     'instead.')

    def destroy_computerate(self, context, computerate_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Computerate, session=session)
            query = add_identity_filter(query, computerate_id)
            count = query.delete()
            if count != 1:
                raise exception.ComputerateNotFound(computerate_id)

    def update_computerate(self, context, computerate_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Computerate.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_computerate_name(context, values['name'])

        return self._do_update_computerate(computerate_id, values)

    def _do_update_computerate(self, computerate_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Computerate, session=session)
            query = add_identity_filter(query, computerate_id)
            LOG.debug('_do_update_computerate xxxxxx computerate_id =%s, query=%s, values=%s',
                      computerate_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.ComputerateNotFound(computerate=computerate_id)

            ref.update(values)
        return ref
