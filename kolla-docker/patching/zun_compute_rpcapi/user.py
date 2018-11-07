    def user_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi user_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'user_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def user_delete(self, context, container, force):
        LOG.debug('rpcapi user_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'user_delete',
                          container=container, force=force)

    #@check_container_host
    def user_show(self, context, container):
        return self._call("", 'user_show',
                          container=container)

    #@check_container_host
    def user_update(self, context, container, patch):
        LOG.debug('user_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'user_update',
                          container=container, patch=patch)

    
