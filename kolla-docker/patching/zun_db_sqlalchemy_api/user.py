    # user section
    def _add_users_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_users(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.User)
        # query = self._add_tenant_filters(context, query)
        query = self._add_users_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_users xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of users is %s', (sort_key))
        return _paginate_query(models.User, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_user_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.User). \
            filter(func.lower(models.User.name) == lowername)
        user_with_same_name = base_query.count()
        if user_with_same_name > 0:
            raise exception.UserAlreadyExists(field='name',
                                                  value=lowername)

    def create_user(self, context, values):
        # ensure defaults are present for new users
        LOG.debug('sqlalchemy api.py create_user xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_user_name(context, values['name'])

        user = models.User()
        user.update(values)
        try:
            user.save()
        except db_exc.DBDuplicateEntry:
            raise exception.UserAlreadyExists(field='name',
                                                  value=values['name'])
        return user

    def get_user_by_uuid(self, context, user_uuid):
        query = model_query(models.User)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=user_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.UserNotFound(user=user_uuid)

    def get_user_by_name(self, context, user_name):
        query = model_query(models.User)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=user_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.UserNotFound(user=user_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple users exist with same '
                                     'name. Please use the user uuid '
                                     'instead.')

    def destroy_user(self, context, user_id):
        session = get_session()
        with session.begin():
            query = model_query(models.User, session=session)
            query = add_identity_filter(query, user_id)
            count = query.delete()
            if count != 1:
                raise exception.UserNotFound(user_id)

    def update_user(self, context, user_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing User.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_user_name(context, values['name'])

        return self._do_update_user(user_id, values)

    def _do_update_user(self, user_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.User, session=session)
            query = add_identity_filter(query, user_id)
            LOG.debug('_do_update_user xxxxxx user_id =%s, query=%s, values=%s',
                      user_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.UserNotFound(user=user_id)

            ref.update(values)
        return ref
