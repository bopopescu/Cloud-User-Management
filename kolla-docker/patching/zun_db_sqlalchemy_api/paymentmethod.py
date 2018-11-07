    # paymentmethod section
    def _add_paymentmethods_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_paymentmethods(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Paymentmethod)
        # query = self._add_tenant_filters(context, query)
        query = self._add_paymentmethods_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_paymentmethods xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of paymentmethods is %s', (sort_key))
        return _paginate_query(models.Paymentmethod, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_paymentmethod_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Paymentmethod). \
            filter(func.lower(models.Paymentmethod.name) == lowername)
        paymentmethod_with_same_name = base_query.count()
        if paymentmethod_with_same_name > 0:
            raise exception.PaymentmethodAlreadyExists(field='name',
                                                  value=lowername)

    def create_paymentmethod(self, context, values):
        # ensure defaults are present for new paymentmethods
        LOG.debug('sqlalchemy api.py create_paymentmethod xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_paymentmethod_name(context, values['name'])

        paymentmethod = models.Paymentmethod()
        paymentmethod.update(values)
        try:
            paymentmethod.save()
        except db_exc.DBDuplicateEntry:
            raise exception.PaymentmethodAlreadyExists(field='name',
                                                  value=values['name'])
        return paymentmethod

    def get_paymentmethod_by_uuid(self, context, paymentmethod_uuid):
        query = model_query(models.Paymentmethod)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=paymentmethod_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.PaymentmethodNotFound(paymentmethod=paymentmethod_uuid)

    def get_paymentmethod_by_name(self, context, paymentmethod_name):
        query = model_query(models.Paymentmethod)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=paymentmethod_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.PaymentmethodNotFound(paymentmethod=paymentmethod_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple paymentmethods exist with same '
                                     'name. Please use the paymentmethod uuid '
                                     'instead.')

    def destroy_paymentmethod(self, context, paymentmethod_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Paymentmethod, session=session)
            query = add_identity_filter(query, paymentmethod_id)
            count = query.delete()
            if count != 1:
                raise exception.PaymentmethodNotFound(paymentmethod_id)

    def update_paymentmethod(self, context, paymentmethod_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Paymentmethod.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_paymentmethod_name(context, values['name'])

        return self._do_update_paymentmethod(paymentmethod_id, values)

    def _do_update_paymentmethod(self, paymentmethod_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Paymentmethod, session=session)
            query = add_identity_filter(query, paymentmethod_id)
            LOG.debug('_do_update_paymentmethod xxxxxx paymentmethod_id =%s, query=%s, values=%s',
                      paymentmethod_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.PaymentmethodNotFound(paymentmethod=paymentmethod_id)

            ref.update(values)
        return ref
