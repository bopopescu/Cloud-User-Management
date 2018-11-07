    def instance_update(self, context, container, *args):
        if direct_action:
            return self.manager.instance_update(context, container, *args)
        else:
            return self.rpcapi.instance_update(context, container, *args)


    def instance_show(self, context, container, *args):
        if direct_action:
            return self.manager.instance_show(context, container)
        else:
            return self.rpcapi.instance_show(context, container)


    def instance_create(self, context, new_instance, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_instance, extra_spec)
        except Exception as exc:
            # new_instance.status = consts.ERROR
            # new_instance.status_reason = str(exc)
            # new_instance.save(context)
            return
        if direct_action:
            self.manager.instance_create(context, "", requested_networks, new_instance)
        else:
            self.rpcapi.instance_create(context, "", new_instance, "", requested_networks)
        # self.rpcapi.instance_create(context, host_state['host'],
        #                             new_instance, host_state['limits'],
        #                             requested_networks)


    def instance_delete(self, context, container, *args):
        return self.manager.instance_delete(context, container, True)
        # return self.rpcapi.instance_delete(context, container, *args)
