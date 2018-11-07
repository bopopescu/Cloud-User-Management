    def usage_update(self, context, container, *args):
        if direct_action:
            return self.manager.usage_update(context, container, *args)
        else:
            return self.rpcapi.usage_update(context, container, *args)


    def usage_show(self, context, container, *args):
        if direct_action:
            return self.manager.usage_show(context, container)
        else:
            return self.rpcapi.usage_show(context, container)


    def usage_create(self, context, new_usage, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_usage, extra_spec)
        except Exception as exc:
            # new_usage.status = consts.ERROR
            # new_usage.status_reason = str(exc)
            # new_usage.save(context)
            return
        if direct_action:
            self.manager.usage_create(context, "", requested_networks, new_usage)
        else:
            self.rpcapi.usage_create(context, "", new_usage, "", requested_networks)
        # self.rpcapi.usage_create(context, host_state['host'],
        #                             new_usage, host_state['limits'],
        #                             requested_networks)


    def usage_delete(self, context, container, *args):
        return self.manager.usage_delete(context, container, True)
        # return self.rpcapi.usage_delete(context, container, *args)
