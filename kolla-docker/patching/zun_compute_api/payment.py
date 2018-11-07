    def payment_update(self, context, container, *args):
        if direct_action:
            return self.manager.payment_update(context, container, *args)
        else:
            return self.rpcapi.payment_update(context, container, *args)


    def payment_show(self, context, container, *args):
        if direct_action:
            return self.manager.payment_show(context, container)
        else:
            return self.rpcapi.payment_show(context, container)


    def payment_create(self, context, new_payment, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_payment, extra_spec)
        except Exception as exc:
            # new_payment.status = consts.ERROR
            # new_payment.status_reason = str(exc)
            # new_payment.save(context)
            return
        if direct_action:
            self.manager.payment_create(context, "", requested_networks, new_payment)
        else:
            self.rpcapi.payment_create(context, "", new_payment, "", requested_networks)
        # self.rpcapi.payment_create(context, host_state['host'],
        #                             new_payment, host_state['limits'],
        #                             requested_networks)


    def payment_delete(self, context, container, *args):
        return self.manager.payment_delete(context, container, True)
        # return self.rpcapi.payment_delete(context, container, *args)
