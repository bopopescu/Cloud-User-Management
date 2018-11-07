    # payment section
    def _add_payments_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_payments(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Payment)
        # query = self._add_tenant_filters(context, query)
        query = self._add_payments_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_payments xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of payments is %s', (sort_key))
        return _paginate_query(models.Payment, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_payment_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Payment). \
            filter(func.lower(models.Payment.name) == lowername)
        payment_with_same_name = base_query.count()
        if payment_with_same_name > 0:
            raise exception.PaymentAlreadyExists(field='name',
                                                  value=lowername)

    def create_payment(self, context, values):
        # ensure defaults are present for new payments
        LOG.debug('sqlalchemy api.py create_payment xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_payment_name(context, values['name'])

        payment = models.Payment()
        payment.update(values)
        try:
            payment.save()
        except db_exc.DBDuplicateEntry:
            raise exception.PaymentAlreadyExists(field='name',
                                                  value=values['name'])
        return payment

    def get_payment_by_uuid(self, context, payment_uuid):
        query = model_query(models.Payment)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=payment_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.PaymentNotFound(payment=payment_uuid)

    def get_payment_by_name(self, context, payment_name):
        query = model_query(models.Payment)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=payment_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.PaymentNotFound(payment=payment_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple payments exist with same '
                                     'name. Please use the payment uuid '
                                     'instead.')

    def destroy_payment(self, context, payment_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Payment, session=session)
            query = add_identity_filter(query, payment_id)
            count = query.delete()
            if count != 1:
                raise exception.PaymentNotFound(payment_id)

    def update_payment(self, context, payment_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Payment.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_payment_name(context, values['name'])

        return self._do_update_payment(payment_id, values)

    def _do_update_payment(self, payment_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Payment, session=session)
            query = add_identity_filter(query, payment_id)
            LOG.debug('_do_update_payment xxxxxx payment_id =%s, query=%s, values=%s',
                      payment_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.PaymentNotFound(payment=payment_id)

            ref.update(values)
        return ref
