from .utils import NamespacedClient, query_params, _make_path

class ClusterClient(NamespacedClient):
    @query_params('level', 'local', 'master_timeout', 'timeout',
        'wait_for_active_shards', 'wait_for_nodes', 'wait_for_relocating_shards',
        'wait_for_status')
    def health(self, index=None, params=None):
        """
        Get a very simple status on the health of the cluster.
        `<http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/cluster-health.html>`_

        :arg index: Limit the information returned to a specific index
        :arg level: Specify the level of detail for returned information, default u'cluster'
        :arg local: Return local information, do not retrieve the state from master node (default: false)
        :arg master_timeout: Explicit operation timeout for connection to master node
        :arg timeout: Explicit operation timeout
        :arg wait_for_active_shards: Wait until the specified number of shards is active
        :arg wait_for_nodes: Wait until the specified number of nodes is available
        :arg wait_for_relocating_shards: Wait until the specified number of relocating shards is finished
        :arg wait_for_status: Wait until cluster is in a specific state, default None
        """
        _, data = self.transport.perform_request('GET', _make_path('_cluster', 'health', index),
            params=params)
        return data

    @query_params('local', 'master_timeout')
    def pending_tasks(self, params=None):
        """
        The pending cluster tasks API returns a list of any cluster-level
        changes (e.g. create index, update mapping, allocate or fail shard)
        which have not yet been executed.
        `<http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/cluster-pending.html>`_

        :arg local: Return local information, do not retrieve the state from master node (default: false)
        :arg master_timeout: Specify timeout for connection to master
        """
        _, data = self.transport.perform_request('GET', '/_cluster/pending_tasks',
            params=params)
        return data

    @query_params('index_templates', 'local', 'master_timeout', 'flat_settings')
    def state(self, metric=None, index=None, params=None):
        """
        Get a comprehensive state information of the whole cluster.
        `<http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/cluster-state.html>`_

        :arg metric: Limit the information returned to the specified metrics.
            Possible values: "_all", "blocks", "index_templates", "metadata",
            "nodes", "routing_table"
        :arg index: A comma-separated list of index names; use `_all` or empty
            string to perform the operation on all indices
        :arg index_templates: A comma separated list to return specific index
            templates when returning metadata.
        :arg local: Return local information, do not retrieve the state from master node (default: false)
        :arg master_timeout: Specify timeout for connection to master
        :arg flat_settings: Return settings in flat format (default: false)
        """
        if index and not metric:
            metric = '_all'
        _, data = self.transport.perform_request('GET', _make_path('_cluster', 'state', metric, index), params=params)
        return data

    @query_params('flat_settings', 'human')
    def stats(self, node_id=None, params=None):
        """
        The Cluster Stats API allows to retrieve statistics from a cluster wide
        perspective. The API returns basic index metrics and information about
        the current nodes that form the cluster.
        `<http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/cluster-stats.html>`_

        :arg node_id: A comma-separated list of node IDs or names to limit the
            returned information; use `_local` to return information from the node
            you're connecting to, leave empty to get information from all nodes
        :arg flat_settings: Return settings in flat format (default: false)
        :arg human: Whether to return time and byte values in human-readable format.

        """
        url = '/_cluster/stats'
        if node_id:
            url = _make_path('_cluster/stats/nodes', node_id)
        _, data = self.transport.perform_request('GET', url, params=params)
        return data

    @query_params('dry_run', 'filter_metadata', 'master_timeout', 'timeout')
    def reroute(self, body=None, params=None):
        """
        Explicitly execute a cluster reroute allocation command including specific commands.
        `<http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/cluster-reroute.html>`_

        :arg body: The definition of `commands` to perform (`move`, `cancel`, `allocate`)
        :arg dry_run: Simulate the operation only and return the resulting state
        :arg filter_metadata: Don't return cluster state metadata (default: false)
        :arg master_timeout: Explicit operation timeout for connection to master node
        :arg timeout: Explicit operation timeout
        """
        _, data = self.transport.perform_request('POST', '/_cluster/reroute', params=params, body=body)
        return data

    @query_params('flat_settings', 'master_timeout', 'timeout')
    def get_settings(self, params=None):
        """
        Get cluster settings.
        `<http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/cluster-update-settings.html>`_

        :arg flat_settings: Return settings in flat format (default: false)
        :arg master_timeout: Explicit operation timeout for connection to master node
        :arg timeout: Explicit operation timeout
        """
        _, data = self.transport.perform_request('GET', '/_cluster/settings', params=params)
        return data

    @query_params('flat_settings')
    def put_settings(self, body, params=None):
        """
        Update cluster wide specific settings.
        `<http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/cluster-update-settings.html>`_

        :arg body: The settings to be updated. Can be either `transient` or
            `persistent` (survives cluster restart).
        :arg flat_settings: Return settings in flat format (default: false)
        """
        _, data = self.transport.perform_request('PUT', '/_cluster/settings', params=params, body=body)
        return data

