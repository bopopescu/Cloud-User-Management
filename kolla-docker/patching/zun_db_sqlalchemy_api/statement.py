    # statement section
    def _add_statements_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_statements(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Statement)
        # query = self._add_tenant_filters(context, query)
        query = self._add_statements_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_statements xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of statements is %s', (sort_key))
        return _paginate_query(models.Statement, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_statement_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Statement). \
            filter(func.lower(models.Statement.name) == lowername)
        statement_with_same_name = base_query.count()
        if statement_with_same_name > 0:
            raise exception.StatementAlreadyExists(field='name',
                                                  value=lowername)

    def create_statement(self, context, values):
        # ensure defaults are present for new statements
        LOG.debug('sqlalchemy api.py create_statement xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_statement_name(context, values['name'])

        statement = models.Statement()
        statement.update(values)
        try:
            statement.save()
        except db_exc.DBDuplicateEntry:
            raise exception.StatementAlreadyExists(field='name',
                                                  value=values['name'])
        return statement

    def get_statement_by_uuid(self, context, statement_uuid):
        query = model_query(models.Statement)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=statement_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.StatementNotFound(statement=statement_uuid)

    def get_statement_by_name(self, context, statement_name):
        query = model_query(models.Statement)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=statement_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.StatementNotFound(statement=statement_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple statements exist with same '
                                     'name. Please use the statement uuid '
                                     'instead.')

    def destroy_statement(self, context, statement_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Statement, session=session)
            query = add_identity_filter(query, statement_id)
            count = query.delete()
            if count != 1:
                raise exception.StatementNotFound(statement_id)

    def update_statement(self, context, statement_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Statement.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_statement_name(context, values['name'])

        return self._do_update_statement(statement_id, values)

    def _do_update_statement(self, statement_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Statement, session=session)
            query = add_identity_filter(query, statement_id)
            LOG.debug('_do_update_statement xxxxxx statement_id =%s, query=%s, values=%s',
                      statement_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.StatementNotFound(statement=statement_id)

            ref.update(values)
        return ref
