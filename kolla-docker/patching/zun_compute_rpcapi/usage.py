    def usage_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi usage_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'usage_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def usage_delete(self, context, container, force):
        LOG.debug('rpcapi usage_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'usage_delete',
                          container=container, force=force)

    #@check_container_host
    def usage_show(self, context, container):
        return self._call("", 'usage_show',
                          container=container)

    #@check_container_host
    def usage_update(self, context, container, patch):
        LOG.debug('usage_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'usage_update',
                          container=container, patch=patch)

    
