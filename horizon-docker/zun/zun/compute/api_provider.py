direct_action=True


def provider_update(self, context, container, *args):
    if direct_action:
        return self.manager.provider_update(context, container, *args)
    else:
        return self.rpcapi.provider_update(context, container, *args)


def provider_show(self, context, container, *args):
    if direct_action:
        return self.manager.provider_show(context, container)
    else:
        return self.rpcapi.provider_show(context, container)


def provider_create(self, context, new_provider, extra_spec,
                    requested_networks):
    host_state = None
    try:
        host_state = {}  # self._schedule_container(context, new_provider, extra_spec)
    except Exception as exc:
        # new_provider.status = consts.ERROR
        # new_provider.status_reason = str(exc)
        # new_provider.save(context)
        return
    if direct_action:
        self.manager.provider_create(context, "", requested_networks, new_provider)
    else:
        self.rpcapi.provider_create(context, "", new_provider, "", requested_networks)
    # self.rpcapi.provider_create(context, host_state['host'],
    #                             new_provider, host_state['limits'],
    #                             requested_networks)


def provider_delete(self, context, container, *args):
    return self.manager.provider_delete(context, container, True)
    # return self.rpcapi.provider_delete(context, container, *args)
