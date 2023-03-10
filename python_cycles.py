from typing import List, Optional, Set, Tuple, TypedDict, Union


TreePackage = TypedDict(
    'TreePackage', {"key": str, "package_name": str, "installed_version": str})
Tree = TypedDict(
    'Tree', {"package": TreePackage, "dependencies": List[Union['Tree', TreePackage]]})


def build_edge_set(pipdeptree_json: List[Union[Tree, TreePackage]]) -> Set[Tuple[str, str]]:
    edges: Set[Tuple[str, str]] = set()

    def index_tree(tree_key: List[int]) -> Optional[Tree | TreePackage]:
        tree = None
        forest = pipdeptree_json
        for index in tree_key:
            try:
                tree = forest[index]
            except (IndexError, TypeError):
                return None

            forest = tree.get('dependencies')

        return tree

    def get_key(tree: Tree | TreePackage):
        key = tree.get('package', {}).get('key') or tree.get('key')
        if not key:
            raise TypeError()
        return key

    tree_key = [0]
    dep_index = 0
    while tree_key:
        subtree: Optional[Tree | TreePackage] = index_tree(tree_key)

        if not subtree:
            tree_key.pop()
            dep_index = 0
            continue

        dep: Optional[Tree | TreePackage] = index_tree(tree_key + [dep_index])

        if not dep:
            tree_key[-1] += 1
            dep_index = 0
            continue

        edges.add((get_key(subtree), get_key(dep)))

        dep_index += 1

    return edges
