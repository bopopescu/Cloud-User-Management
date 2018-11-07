    def providerregion_update(self, context, container, *args):
        if direct_action:
            return self.manager.providerregion_update(context, container, *args)
        else:
            return self.rpcapi.providerregion_update(context, container, *args)


    def providerregion_show(self, context, container, *args):
        if direct_action:
            return self.manager.providerregion_show(context, container)
        else:
            return self.rpcapi.providerregion_show(context, container)


    def providerregion_create(self, context, new_providerregion, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_providerregion, extra_spec)
        except Exception as exc:
            # new_providerregion.status = consts.ERROR
            # new_providerregion.status_reason = str(exc)
            # new_providerregion.save(context)
            return
        if direct_action:
            self.manager.providerregion_create(context, "", requested_networks, new_providerregion)
        else:
            self.rpcapi.providerregion_create(context, "", new_providerregion, "", requested_networks)
        # self.rpcapi.providerregion_create(context, host_state['host'],
        #                             new_providerregion, host_state['limits'],
        #                             requested_networks)


    def providerregion_delete(self, context, container, *args):
        return self.manager.providerregion_delete(context, container, True)
        # return self.rpcapi.providerregion_delete(context, container, *args)
