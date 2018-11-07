    def statement_update(self, context, container, *args):
        if direct_action:
            return self.manager.statement_update(context, container, *args)
        else:
            return self.rpcapi.statement_update(context, container, *args)


    def statement_show(self, context, container, *args):
        if direct_action:
            return self.manager.statement_show(context, container)
        else:
            return self.rpcapi.statement_show(context, container)


    def statement_create(self, context, new_statement, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_statement, extra_spec)
        except Exception as exc:
            # new_statement.status = consts.ERROR
            # new_statement.status_reason = str(exc)
            # new_statement.save(context)
            return
        if direct_action:
            self.manager.statement_create(context, "", requested_networks, new_statement)
        else:
            self.rpcapi.statement_create(context, "", new_statement, "", requested_networks)
        # self.rpcapi.statement_create(context, host_state['host'],
        #                             new_statement, host_state['limits'],
        #                             requested_networks)


    def statement_delete(self, context, container, *args):
        return self.manager.statement_delete(context, container, True)
        # return self.rpcapi.statement_delete(context, container, *args)
