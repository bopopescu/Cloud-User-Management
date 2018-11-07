    def computerate_update(self, context, container, *args):
        if direct_action:
            return self.manager.computerate_update(context, container, *args)
        else:
            return self.rpcapi.computerate_update(context, container, *args)


    def computerate_show(self, context, container, *args):
        if direct_action:
            return self.manager.computerate_show(context, container)
        else:
            return self.rpcapi.computerate_show(context, container)


    def computerate_create(self, context, new_computerate, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_computerate, extra_spec)
        except Exception as exc:
            # new_computerate.status = consts.ERROR
            # new_computerate.status_reason = str(exc)
            # new_computerate.save(context)
            return
        if direct_action:
            self.manager.computerate_create(context, "", requested_networks, new_computerate)
        else:
            self.rpcapi.computerate_create(context, "", new_computerate, "", requested_networks)
        # self.rpcapi.computerate_create(context, host_state['host'],
        #                             new_computerate, host_state['limits'],
        #                             requested_networks)


    def computerate_delete(self, context, container, *args):
        return self.manager.computerate_delete(context, container, True)
        # return self.rpcapi.computerate_delete(context, container, *args)
