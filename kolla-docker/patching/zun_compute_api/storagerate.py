    def storagerate_update(self, context, container, *args):
        if direct_action:
            return self.manager.storagerate_update(context, container, *args)
        else:
            return self.rpcapi.storagerate_update(context, container, *args)


    def storagerate_show(self, context, container, *args):
        if direct_action:
            return self.manager.storagerate_show(context, container)
        else:
            return self.rpcapi.storagerate_show(context, container)


    def storagerate_create(self, context, new_storagerate, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_storagerate, extra_spec)
        except Exception as exc:
            # new_storagerate.status = consts.ERROR
            # new_storagerate.status_reason = str(exc)
            # new_storagerate.save(context)
            return
        if direct_action:
            self.manager.storagerate_create(context, "", requested_networks, new_storagerate)
        else:
            self.rpcapi.storagerate_create(context, "", new_storagerate, "", requested_networks)
        # self.rpcapi.storagerate_create(context, host_state['host'],
        #                             new_storagerate, host_state['limits'],
        #                             requested_networks)


    def storagerate_delete(self, context, container, *args):
        return self.manager.storagerate_delete(context, container, True)
        # return self.rpcapi.storagerate_delete(context, container, *args)
