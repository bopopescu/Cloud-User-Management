    def providervm_update(self, context, container, *args):
        if direct_action:
            return self.manager.providervm_update(context, container, *args)
        else:
            return self.rpcapi.providervm_update(context, container, *args)


    def providervm_show(self, context, container, *args):
        if direct_action:
            return self.manager.providervm_show(context, container)
        else:
            return self.rpcapi.providervm_show(context, container)


    def providervm_create(self, context, new_providervm, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_providervm, extra_spec)
        except Exception as exc:
            # new_providervm.status = consts.ERROR
            # new_providervm.status_reason = str(exc)
            # new_providervm.save(context)
            return
        if direct_action:
            self.manager.providervm_create(context, "", requested_networks, new_providervm)
        else:
            self.rpcapi.providervm_create(context, "", new_providervm, "", requested_networks)
        # self.rpcapi.providervm_create(context, host_state['host'],
        #                             new_providervm, host_state['limits'],
        #                             requested_networks)


    def providervm_delete(self, context, container, *args):
        return self.manager.providervm_delete(context, container, True)
        # return self.rpcapi.providervm_delete(context, container, *args)
