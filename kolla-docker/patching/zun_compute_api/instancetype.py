    def instancetype_update(self, context, container, *args):
        if direct_action:
            return self.manager.instancetype_update(context, container, *args)
        else:
            return self.rpcapi.instancetype_update(context, container, *args)


    def instancetype_show(self, context, container, *args):
        if direct_action:
            return self.manager.instancetype_show(context, container)
        else:
            return self.rpcapi.instancetype_show(context, container)


    def instancetype_create(self, context, new_instancetype, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_instancetype, extra_spec)
        except Exception as exc:
            # new_instancetype.status = consts.ERROR
            # new_instancetype.status_reason = str(exc)
            # new_instancetype.save(context)
            return
        if direct_action:
            self.manager.instancetype_create(context, "", requested_networks, new_instancetype)
        else:
            self.rpcapi.instancetype_create(context, "", new_instancetype, "", requested_networks)
        # self.rpcapi.instancetype_create(context, host_state['host'],
        #                             new_instancetype, host_state['limits'],
        #                             requested_networks)


    def instancetype_delete(self, context, container, *args):
        return self.manager.instancetype_delete(context, container, True)
        # return self.rpcapi.instancetype_delete(context, container, *args)
