    def user_update(self, context, container, *args):
        if direct_action:
            return self.manager.user_update(context, container, *args)
        else:
            return self.rpcapi.user_update(context, container, *args)


    def user_show(self, context, container, *args):
        if direct_action:
            return self.manager.user_show(context, container)
        else:
            return self.rpcapi.user_show(context, container)


    def user_create(self, context, new_user, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_user, extra_spec)
        except Exception as exc:
            # new_user.status = consts.ERROR
            # new_user.status_reason = str(exc)
            # new_user.save(context)
            return
        if direct_action:
            self.manager.user_create(context, "", requested_networks, new_user)
        else:
            self.rpcapi.user_create(context, "", new_user, "", requested_networks)
        # self.rpcapi.user_create(context, host_state['host'],
        #                             new_user, host_state['limits'],
        #                             requested_networks)


    def user_delete(self, context, container, *args):
        return self.manager.user_delete(context, container, True)
        # return self.rpcapi.user_delete(context, container, *args)
