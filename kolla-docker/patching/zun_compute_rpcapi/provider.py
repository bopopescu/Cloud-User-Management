    def provider_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi provider_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'provider_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def provider_delete(self, context, container, force):
        LOG.debug('rpcapi provider_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'provider_delete',
                          container=container, force=force)

    #@check_container_host
    def provider_show(self, context, container):
        return self._call("", 'provider_show',
                          container=container)

    #@check_container_host
    def provider_update(self, context, container, patch):
        LOG.debug('provider_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'provider_update',
                          container=container, patch=patch)

    
