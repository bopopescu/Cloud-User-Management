    def paymentmethod_update(self, context, container, *args):
        if direct_action:
            return self.manager.paymentmethod_update(context, container, *args)
        else:
            return self.rpcapi.paymentmethod_update(context, container, *args)


    def paymentmethod_show(self, context, container, *args):
        if direct_action:
            return self.manager.paymentmethod_show(context, container)
        else:
            return self.rpcapi.paymentmethod_show(context, container)


    def paymentmethod_create(self, context, new_paymentmethod, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_paymentmethod, extra_spec)
        except Exception as exc:
            # new_paymentmethod.status = consts.ERROR
            # new_paymentmethod.status_reason = str(exc)
            # new_paymentmethod.save(context)
            return
        if direct_action:
            self.manager.paymentmethod_create(context, "", requested_networks, new_paymentmethod)
        else:
            self.rpcapi.paymentmethod_create(context, "", new_paymentmethod, "", requested_networks)
        # self.rpcapi.paymentmethod_create(context, host_state['host'],
        #                             new_paymentmethod, host_state['limits'],
        #                             requested_networks)


    def paymentmethod_delete(self, context, container, *args):
        return self.manager.paymentmethod_delete(context, container, True)
        # return self.rpcapi.paymentmethod_delete(context, container, *args)
