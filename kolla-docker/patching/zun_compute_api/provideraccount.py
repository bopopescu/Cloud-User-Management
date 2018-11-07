    def provideraccount_update(self, context, container, *args):
        if direct_action:
            return self.manager.provideraccount_update(context, container, *args)
        else:
            return self.rpcapi.provideraccount_update(context, container, *args)


    def provideraccount_show(self, context, container, *args):
        if direct_action:
            return self.manager.provideraccount_show(context, container)
        else:
            return self.rpcapi.provideraccount_show(context, container)


    def provideraccount_create(self, context, new_provideraccount, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_provideraccount, extra_spec)
        except Exception as exc:
            # new_provideraccount.status = consts.ERROR
            # new_provideraccount.status_reason = str(exc)
            # new_provideraccount.save(context)
            return
        if direct_action:
            self.manager.provideraccount_create(context, "", requested_networks, new_provideraccount)
        else:
            self.rpcapi.provideraccount_create(context, "", new_provideraccount, "", requested_networks)
        # self.rpcapi.provideraccount_create(context, host_state['host'],
        #                             new_provideraccount, host_state['limits'],
        #                             requested_networks)


    def provideraccount_delete(self, context, container, *args):
        return self.manager.provideraccount_delete(context, container, True)
        # return self.rpcapi.provideraccount_delete(context, container, *args)
