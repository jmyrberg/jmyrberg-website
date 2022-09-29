"""Module for maximum flows."""


import functools
import os

from flask import jsonify
from itsdangerous import Signer

from ortools.graph.python.max_flow import SimpleMaxFlow


def request_wrapper(original_func=None,
                    allowed_methods=frozenset(['GET', 'PUT', 'OPTIONS', 'POST',
                                               'DELETE'])):
    def _decorate(func):
        @functools.wraps(func)
        def wrapped_func(request):
            # Request legitimity
            headers = None
            if request.method not in allowed_methods:
                return jsonify({'status': 'error',
                                'message': 'Method not allowed',
                                'data': None}), 403
            if request.method == 'OPTIONS':
                headers = {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': allowed_methods,
                    'Access-Control-Allow-Headers': ['Content-Type',
                                                     'x-api-key'],
                    'Access-Control-Max-Age': '3600',
                }
                return ('', 204, headers)
            else:
                headers = {'Access-Control-Allow-Origin': '*'}
            # Token
            api_key = request.headers.get('X-API-KEY')
            if not api_key:
                return jsonify({'status': 'error',
                                'message': 'Missing "x-api-key" header',
                                'data': None}), 401
            else:
                try:
                    Signer(os.environ['SECRET_KEY']).unsign(api_key)
                except Exception:
                    return jsonify({'status': 'error',
                                    'message': 'Invalid access token',
                                    'data': None}), 401
            # Function call or error
            try:
                resp, status = func(request)
                return jsonify(resp), status, headers
            except Exception as e:
                return jsonify({'status': 'error',
                                'message': str(e),
                                'data': None}), 500, headers
        return wrapped_func

    if original_func:
        return _decorate(original_func)

    return _decorate


@request_wrapper(allowed_methods=['OPTIONS', 'POST'])
def maximum_flows(request):
    """Solve maximum flow optimization problem.

    Args:
        data (dict): Input data as defined in the endpoint.

    References:
        https://developers.google.com/optimization/flow/maxflow
    """
    # Get inputs
    print('Starting maximum flow optimization...')
    data = request.get_json()['data']
    start_nodes = [arc['startNodeId'] for arc in data['arcs']]
    end_nodes = [arc['endNodeId'] for arc in data['arcs']]
    capacities = [arc['capacity'] for arc in data['arcs']]
    source_node = [n['id'] for n in data['nodes'] if n['type'] == 'Source'][0]
    sink_node = [n['id'] for n in data['nodes'] if n['type'] == 'Sink'][0]

    # Map nodes
    unique_nodes = set(start_nodes + end_nodes)
    node_map = dict((v, i) for i, v in enumerate(unique_nodes))
    node_inv_map = dict((i, k) for k, i in node_map.items())
    start_nodes = [node_map[n] for n in start_nodes]
    end_nodes = [node_map[n] for n in end_nodes]
    source_node = node_map[source_node]
    sink_node = node_map[sink_node]

    # Optimize
    max_flow = SimpleMaxFlow()
    max_flow.add_arcs_with_capacity(start_nodes, end_nodes, capacities)
    solved = max_flow.solve(source_node, sink_node)

    # Results
    status = 'success'
    message = None
    data = None
    if solved == max_flow.OPTIMAL:
        message = 'Optimal solution found successfully!'
        data = {}
        data['optimalFlow'] = max_flow.optimal_flow()
        data['sourceMinCut'] = [node_inv_map[i]
                                for i in max_flow.get_source_side_min_cut()]
        data['sinkMinCut'] = [node_inv_map[i]
                              for i in max_flow.get_sink_side_min_cut()]
        data['arcs'] = []
        for i in range(max_flow.num_arcs()):
            data['arcs'].append({
                'startNodeId': node_inv_map[max_flow.tail(i)],
                'endNodeId': node_inv_map[max_flow.head(i)],
                'flow': max_flow.flow(i),
                'capacity': max_flow.capacity(i)
            })
    else:
        message = 'No solution found'

    return {'status': status, 'message': message, 'data': data}, 200
