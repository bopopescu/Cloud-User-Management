    def payment_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi payment_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'payment_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def payment_delete(self, context, container, force):
        LOG.debug('rpcapi payment_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'payment_delete',
                          container=container, force=force)

    #@check_container_host
    def payment_show(self, context, container):
        return self._call("", 'payment_show',
                          container=container)

    #@check_container_host
    def payment_update(self, context, container, patch):
        LOG.debug('payment_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'payment_update',
                          container=container, patch=patch)

    
