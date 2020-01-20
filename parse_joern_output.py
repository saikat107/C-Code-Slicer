import os, sys, argparse
from graphviz import Digraph


def read_csv(csv_file_path):
    data = []
    with open(csv_file_path) as fp:
        header = fp.readline()
        header = header.strip()
        h_parts = [hp.strip() for hp in header.split('\t')]
        for line in fp:
            line = line.strip()
            instance = {}
            lparts = line.split('\t')
            for i, hp in enumerate(h_parts):
                if i < len(lparts):
                    content = lparts[i].strip()
                else:
                    content = ''
                instance[hp] = content
            data.append(instance)
        return data


def read_code_file(file_path):
    code_lines = {}
    with open(file_path) as fp:
        for ln, line in enumerate(fp):
            line = line.strip()
            code_lines[ln + 1] = line
        return code_lines


def extract_nodes_with_location_info(nodes):
    # Will return an array identifying the indices of those nodes in nodes array,
    # another array identifying the node_id of those nodes
    # another array indicating the line numbers
    # all 3 return arrays should have same length indicating 1-to-1 matching.
    node_indices = []
    node_ids = []
    line_numbers = []
    node_id_to_line_number = {}
    for node_index, node in enumerate(nodes):
        assert isinstance(node, dict)
        if 'location' in node.keys():
            location = node['location']
            if location == '':
                continue
            # if node['isCFGNode'] == '':
            #     continue
            line_num = int(location.split(':')[0])
            node_id = node['key'].strip()
            node_indices.append(node_index)
            node_ids.append(node_id)
            line_numbers.append(line_num)
            node_id_to_line_number[node_id] = line_num
    return node_indices, node_ids, line_numbers, node_id_to_line_number
    pass


def create_adjacency_list(line_numbers, node_id_to_line_numbers, edges):
    adjacency_list = {}
    for ln in set(line_numbers):
        adjacency_list[ln] = [set(), set(), set()]
    for edge in edges:
        edge_type = edge['type'].strip()
        if True:#edge_type in ['IS_AST_PARENT', 'FLOWS_TO']:
            start_node_id = edge['start'].strip()
            end_node_id = edge['end'].strip()
            if start_node_id not in node_id_to_line_numbers.keys() or end_node_id not in node_id_to_line_numbers.keys():
                continue
            start_ln = node_id_to_line_numbers[start_node_id]
            end_ln = node_id_to_line_numbers[end_node_id]
            if edge_type == 'FLOWS_TO': #Control Flow edges
                adjacency_list[start_ln][0].add(end_ln)
            elif edge_type == 'REACHES': # Data Flow edges
                adjacency_list[start_ln][1].add(end_ln)
            else:
                adjacency_list[start_ln][2].add(end_ln)
    return adjacency_list


def create_visual_graph(code, adjacency_list):
    graph = Digraph('Code Property Graph')
    for ln in adjacency_list:
        graph.node(str(ln), code[ln], shape='box')
        control_dependency, data_dependency, others = adjacency_list[ln]
        for anode in control_dependency:
            graph.edge(str(ln), str(anode), color='red')
        for anode in data_dependency:
            graph.edge(str(ln), str(anode), color='blue')
        # for anode in others:
        #     graph.edge(str(ln), str(anode), color='orange')
    print(graph.source)
    graph.render('Graph', view=True)


def create_forward_slice(adjacency_list, line_no):
    sliced_lines = set()
    sliced_lines.add(line_no)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    directory = 'test-joern-parse'
    file_name = 'test1.c'
    code_file_path = os.path.join(directory, file_name)
    nodes_path = os.path.join('parsed', directory, file_name, 'nodes.csv')
    edges_path = os.path.join('parsed', directory, file_name, 'edges.csv')
    nodes = read_csv(nodes_path)
    edges = read_csv(edges_path)
    code = read_code_file(code_file_path)
    node_indices, node_ids, line_numbers, node_id_to_ln = extract_nodes_with_location_info(nodes)
    adjacency_list = create_adjacency_list(line_numbers, node_id_to_ln, edges)
    create_visual_graph(code, adjacency_list)
    print(len(nodes), len(edges), len(code))
    print(nodes[0].keys())
    print(edges[0].keys())


    pass