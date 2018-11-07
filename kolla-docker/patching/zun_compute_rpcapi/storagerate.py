    def storagerate_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi storagerate_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'storagerate_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def storagerate_delete(self, context, container, force):
        LOG.debug('rpcapi storagerate_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'storagerate_delete',
                          container=container, force=force)

    #@check_container_host
    def storagerate_show(self, context, container):
        return self._call("", 'storagerate_show',
                          container=container)

    #@check_container_host
    def storagerate_update(self, context, container, patch):
        LOG.debug('storagerate_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'storagerate_update',
                          container=container, patch=patch)

    
