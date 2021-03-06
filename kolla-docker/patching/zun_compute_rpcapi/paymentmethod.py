    def paymentmethod_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi paymentmethod_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'paymentmethod_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def paymentmethod_delete(self, context, container, force):
        LOG.debug('rpcapi paymentmethod_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'paymentmethod_delete',
                          container=container, force=force)

    #@check_container_host
    def paymentmethod_show(self, context, container):
        return self._call("", 'paymentmethod_show',
                          container=container)

    #@check_container_host
    def paymentmethod_update(self, context, container, patch):
        LOG.debug('paymentmethod_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'paymentmethod_update',
                          container=container, patch=patch)

    
