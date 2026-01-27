# Author : Vamsi Nayank
# Context: ANSA (Python) on NASTRAN deck
# Purpose: Detect weld groups, classify Lap vs T joints, build Side A/B/C sets,
#          and assign elements to global output sets (M*) with fixed SIDs.

import ansa
from ansa import base, constants
import math
from collections import defaultdict, deque


def find_sets_by_name(deck):
    name_to_set = {}
    all_sets = base.CollectEntities(deck, None, "SET") or []
    for s in all_sets:
        vals = base.GetEntityCardValues(deck, s, ("Name",))
        name = vals.get("Name")
        if name:
            name_to_set[name] = s
    return name_to_set


def set_is_empty(deck, set_ent):
    contents = base.CollectEntities(deck, set_ent, "__ALL_ENTITIES__") or []
    return len(contents) == 0


def delete_sets(deck, delete_all_names, delete_if_empty_names):
    name_to_set = find_sets_by_name(deck)

    for nm in delete_all_names:
        s = name_to_set.get(nm)
        if s:
            base.DeleteEntity(s)

    for nm in delete_if_empty_names:
        s = name_to_set.get(nm)
        if not s:
            continue
        if set_is_empty(deck, s):
            base.DeleteEntity(s)


SET_A = "Lap_Joint_delt_Side_A"
SET_B = "Lap_Joint_delt_Side_B"
SET_C = "Lap_Joint_delt_Side_C"
SET_T = "Lap_Joint_delt"


OUT_SETS = {
    "M450": 450,
    "M453": 453,
    "M451": 451,
    "M452": 452,
    "M454": 454,
    "M455": 455,
}


EPS = 1e-9


def get_set_by_name(deck, name):
    for s in base.CollectEntities(deck, None, "SET"):
        card = base.GetEntityCardValues(deck, s, ("Name", "SID"))
        if card and card.get("Name") == name:
            return s
    return None


def ensure_clean_global_sets(deck, out_defs):
    # ###########################
    ids = set(out_def.values())
    for s in base.CollectEntities(deck, None, "SET"):
        card = base.GetEntityCardValues(deck, s, ("SID",))
        if card and card.get("SID") in ids:
            base.DeleteEntity(s)

    created = {}
    for name, sid in out_def.items():
        ent = base.CreateEntity(deck, "SET", {"Name": name, "SID": sid})
        if not ent:
            raise RuntimeError(f"Failed to create SET '{name}' with ID {sid}.")
        created[name] = ent

    return created


def collect_visible_shells(deck, container_entity):
    return base.CollectEntities(
        deck,
        container_entity,
        "SHELL",
        filter_visible=True,
        recursive=True
    )


def get_elem_grids(deck, elem):
    keys = ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8")
    vals = base.GetEntityCardValues(deck, elem, keys)
    grids = [vals[k] for k in keys if k in vals and vals[k]]
    return [gid for gid in grids if gid and gid != 0]


def get_grid_coords(deck, grid_id):
    grid = base.GetEntity(deck, "GRID", grid_id)
    if not grid:
        return None

    card = base.GetEntityCardValues(deck, grid, ("X1", "X2", "X3"))
    x1 = card.get("X1")
    x2 = card.get("X2")
    x3 = card.get("X3")

    if x1 is None or x2 is None or x3 is None:
        return None

    return (x1, x2, x3)


def v_sub(a, b):
    if a is None or b is None:
        return None
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def v_len(a):
    if a is None:
        return 0.0
    return math.sqrt(a[0]*a[0] + a[1]*a[1] + a[2]*a[2])


def v_norm(a):
    L = v_len(a)
    if L <= EPS:
        return None
    return (a[0]/L, a[1]/L, a[2]/L)


def v_dot(a, b):
    if a is None or b is None:
        return None
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]


def normal_of_shell(elem):
    n = base.GetNormalVectorOfShell(elem)
    return v_norm(n) if n is not None else None


def build_union_and_labels(deck):
    sets = {
        "A": get_set_by_name(deck, SET_A),
        "B": get_set_by_name(deck, SET_B),
        "C": get_set_by_name(deck, SET_C),
        "T": get_set_by_name(deck, SET_T),
    }

    for lbl, s in sets.items():
        if not s:
            raise ValueError(f"SET for label '{lbl}' not found.")

    shells_by_label = {
        lbl: collect_visible_shells(deck, s)
        for lbl, s in sets.items()
    }

    union_shells = []
    labels_map = {}
    seen = set()

    for lbl in ("A", "B", "C", "T"):
        for e in shells_by_label[lbl]:
            if e not in seen:
                seen.add(e)
                union_shells.append(e)
                labels_map.setdefault(e, set()).add(lbl)

    return union_shells, labels_map


def build_grid_to_elems(deck, elems):
    elem_grids = {}
    grid_to_elems = defaultdict(list)

    for e in elems:
        grids = get_elem_grids(deck, e)
        elem_grids[e] = grids
        for gid in grids:
            grid_to_elems[gid].append(e)

    return grid_to_elems, elem_grids


def build_adjacency_any_grid(elems, elem_grids):
    grid_to_elems = defaultdict(list)

    for e, grids in elem_grids.items():
        for g in grids:
            grid_to_elems[g].append(e)

    adj = {e: set() for e in elems}

    for owners in grid_to_elems.values():
        if len(owners) > 1:
            for i in range(len(owners)):
                for j in range(i + 1, len(owners)):
                    a, b = owners[i], owners[j]
                    adj[a].add(b)
                    adj[b].add(a)

    return adj


def connected_components(adj, elems):
    visited = set()
    comps = []

    for e in elems:
        if e in visited:
            continue

        q = deque([e])
        comp = []
        visited.add(e)

        while q:
            u = q.popleft()
            comp.append(u)
            for v in adj[u]:
                if v not in visited:
                    visited.add(v)
                    q.append(v)

        comps.append(comp)

    return comps

def find_triplet_centers_for_group(comp, grid_to_elems, labels_map):
    comp_set = set(comp)
    centers = []

    for gid, owners in grid_to_elems.items():
        owners_in_comp = [e for e in owners if e in comp_set]
        if not owners_in_comp:
            continue

        cntA = cntB = cntT = cntC = 0
        for e in owners_in_comp:
            lbls = labels_map.get(e, set())
            if "A" in lbls:
                cntA += 1
            if "B" in lbls:
                cntB += 1
            if "T" in lbls:
                cntT += 1
            if "C" in lbls:
                cntC += 1

        if cntA == 1 and cntB == 1 and cntT == 1 and cntC == 0:
            centers.append(gid)

    return centers


def classify_and_assign_group(
    deck,
    comp,
    center_gid,
    grid_to_elems,
    labels_map,
    elem_grids,
    out_sets
):
    center_xyz = get_grid_coords(deck, center_gid)
    if center_xyz is None:
        print("  Skip Below Group for LAP Element Set : center node has no X1/X2/X3")
        return False

    owners_center = [e for e in grid_to_elems[center_gid] if e in comp]

    a_elem = next((e for e in owners_center if "A" in labels_map.get(e, set())), None)
    b_elem = next((e for e in owners_center if "B" in labels_map.get(e, set())), None)
    t_elem = next((e for e in owners_center if "T" in labels_map.get(e, set())), None)

    if not a_elem or not b_elem or not t_elem:
        print("  Skip Below Group for LAP Element Set : cannot resolve A/B/T shells at center")
        return False

    c_edge_gid = None
    c_elem = None

    for gid in elem_grids[t_elem]:
        if gid == center_gid:
            continue

        owners_n = [e for e in grid_to_elems.get(gid, []) if e in comp]
        if len(owners_n) != 2:
            continue

        if t_elem in owners_n:
            other = owners_n[0] if owners_n[1] == t_elem else owners_n[1]
            if "C" in labels_map.get(other, set()):
                c_edge_gid = gid
                c_elem = other
                break

    if c_edge_gid is None or c_elem is None:
        print("  Skip Below Group for LAP Element Set : no C-edge node (exactly t + C)")
        return False

    c_edge_xyz = get_grid_coords(deck, c_edge_gid)
    if c_edge_xyz is None:
        print("  Skip Below Group for LAP Element Set : C-edge node has no X1/X2/X3")
        return False

    c_corner_gid = None
    for gid in elem_grids[c_elem]:
        if gid == c_edge_gid:
            continue

        owners_n = [e for e in grid_to_elems.get(gid, []) if e in comp]
        if len(owners_n) == 1 and owners_n[0] == c_elem:
            c_corner_gid = gid
            break

    if c_corner_gid is None:
        print("  Skip Below Group for LAP Element Set : no C-corner node (exactly one shell: the same side_C)")
        return False

    c_corner_xyz = get_grid_coords(deck, c_corner_gid)
    if c_corner_xyz is None:
        print("  Skip Below Group for LAP Element Set : C-corner node has no X1/X2/X3")
        return False

    a_corner_gid = None
    for gid in elem_grids[a_elem]:
        if gid == center_gid:
            continue

        owners_n = [e for e in grid_to_elems.get(gid, []) if e in comp]
        if len(owners_n) == 1 and owners_n[0] == a_elem:
            a_corner_gid = gid
            break

    if a_corner_gid is None:
        print("  Skip Below Group for LAP Element Set : no A-corner node (exactly one shell: side_A)")
        return False

    a_corner_xyz = get_grid_coords(deck, a_corner_gid)
    if a_corner_xyz is None:
        print("  Skip Below Group for LAP Element Set : A-corner node has no X1/X2/X3")
        return False

    center_C_vec = v_norm(v_sub(c_edge_xyz, center_xyz))
    center_A_vec = v_norm(v_sub(a_corner_xyz, center_xyz))
    edgeCorner_C = v_norm(v_sub(c_corner_xyz, c_edge_xyz))

    if center_C_vec is None or center_A_vec is None or edgeCorner_C is None:
        print("  Skip Below Group for LAP Element Set : vectors undefined")
        return False

    n_C = normal_of_shell(c_elem)
    n_A = normal_of_shell(a_elem)
    n_B = normal_of_shell(b_elem)

    if n_C is None or n_A is None or n_B is None:
        print("  Skip Below Group for LAP Element Set : ANSA shell normals unavailable")
        return False

    same_C_vs_nC = (v_dot(center_C_vec, n_C) > EPS)
    same_C_vs_nA = (v_dot(edgeCorner_C, center_A_vec) > EPS)
    same_C_vs_nB = (v_dot(center_C_vec, n_B) > EPS)
    same_A_vs_nB = (v_dot(center_A_vec, n_B) > EPS)

    comp_A = [e for e in comp if "A" in labels_map.get(e, set())]
    comp_B = [e for e in comp if "B" in labels_map.get(e, set())]
    comp_C = [e for e in comp if "C" in labels_map.get(e, set())]

    base.AddToSet(out_sets["M453" if same_C_vs_nC else "M450"], comp_C)
    key = (same_C_vs_nC, same_C_vs_nA, same_A_vs_nB)

    side_map = {
        (True,  True,  True):  ("M452", "M453"),
        (True,  True,  False): ("M452", "M453"),
        (True,  False, True):  ("M453", "M452"),
        (True,  False, False): ("M453", "M452"),
        (False, True,  True):  ("M451", "M454"),
        (False, True,  False): ("M451", "M454"),
        (False, False, True):  ("M454", "M451"),
        (False, False, False): ("M454", "M451"),
    }

    a_set_name, b_set_name = side_map[key]

    base.AddToSet(out_sets[a_set_name], comp_A)
    base.AddToSet(out_sets[b_set_name], comp_B)

    return True


def run_lap_assignment(deck):
    out_sets = ensure_clean_global_sets(deck, OUT_SETS)

    union_shells, labels_map = build_union_and_labels(deck)
    if not union_shells:
        print("No visible shells found across the lap sets.")
        return

    grid_to_elems, elem_grids = build_grid_to_elems(deck, union_shells)
    adj = build_adjacency_any_grid(union_shells, elem_grids)
    comps = connected_components(adj, union_shells)

    for i, comp in enumerate(comps, start=1):
        comp = [e for e in comp]
        centers = find_triplet_centers_for_group(comp, grid_to_elems, labels_map)

        if not centers:
            print(f"  Skip Below Group for LAP Element Set : no centers node found")
            print(f"  Orphan Element Group [{i}] (skip)")
            continue

        center_gid = centers[0]
        ok = classify_and_assign_group(
            deck,
            comp,
            center_gid,
            grid_to_elems,
            labels_map,
            elem_grids,
            out_sets
        )

        if not ok:
            print(f"Orphan Element Group [{i}] (skip)")


SET_A = "Lap_Joint_delt_Side_A"
SET_B = "Lap_Joint_delt_Side_B"
SET_C = "Lap_Joint_delt_Side_C"
SET_T = "Lap_Joint_delt"

OUT_SETS = {
    "M450": 450,
    "M451": 451,
    "M452": 452,
    "M453": 453,
    "M454": 454,
    "M455": 455,
}

EPS = 1e-9

def get_set_by_name_T(deck, name):
    for s in base.CollectEntities(deck, None, "SET"):
        card = base.GetEntityCardValues(deck, s, ("Name", "SID"))
        if card and card.get("Name") == name:
            return s
    return None


def get_or_create_global_set_T(deck, name, set_id):
    s = get_set_by_name_T(deck, name)
    if s:
        return s
    return base.CreateEntity(deck, "SET", {"Name": name, "SID": set_id})


def collect_visible_shells_T(deck, container_entity):
    return base.CollectEntities(
        deck,
        container_entity,
        "SHELL",
        filter_visible=True,
        recursive=True
    )


def get_elem_grids_T(deck, elem):
    keys = ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8")
    vals = base.GetEntityCardValues(deck, elem, keys)
    grids = [vals[k] for k in keys if k in vals and vals[k]]
    return [gid for gid in grids if gid and gid != 0]


def get_grid_coords_T(deck, grid_id):
    if not grid_id or grid_id == 0:
        return None

    grid = base.GetEntity(deck, "GRID", grid_id)
    if not grid:
        return None

    card = base.GetEntityCardValues(deck, grid, ("X1", "X2", "X3"))
    x1 = card.get("X1")
    x2 = card.get("X2")
    x3 = card.get("X3")

    if x1 is None or x2 is None or x3 is None:
        return None

    return (x1, x2, x3)


def v_sub_T(a, b):
    if a is None or b is None:
        return None
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def v_len_T(a):
    if a is None:
        return 0.0
    return math.sqrt(a[0]*a[0] + a[1]*a[1] + a[2]*a[2])


def v_norm_T(a):
    L = v_len_T(a)
    if L <= EPS:
        return None
    return (a[0]/L, a[1]/L, a[2]/L)


def v_dot_T(a, b):
    if a is None or b is None:
        return None
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2)


def normal_of_shell_T(elem):
    n = base.GetNormalVectorOfShell(elem)
    return v_norm_T(n) if n is not None else None

def build_union_and_labels_T(deck):
    sets = {
        "A": get_set_by_name_T(deck, SET_A),
        "B": get_set_by_name_T(deck, SET_B),
        "C": get_set_by_name_T(deck, SET_C),
        "T": get_set_by_name_T(deck, SET_T),
    }

    for lbl, s in sets.items():
        if not s:
            raise ValueError(f"SET for label '{lbl}' not found.")

    shells_by_label = {
        lbl: collect_visible_shells_T(deck, s)
        for lbl, s in sets.items()
    }

    union_shells = []
    labels_map = {}
    seen = set()

    for lbl in ("A", "B", "C", "T"):
        for e in shells_by_label[lbl]:
            if e not in seen:
                seen.add(e)
                union_shells.append(e)
                labels_map.setdefault(e, set()).add(lbl)

    return union_shells, labels_map


def build_grid_to_elems_T(deck, elems):
    elem_grids = {}
    grid_to_elems = defaultdict(list)

    for e in elems:
        grids = get_elem_grids_T(deck, e)
        elem_grids[e] = grids
        for gid in grids:
            grid_to_elems[gid].append(e)

    return grid_to_elems, elem_grids


def build_adjacency_any_grid_T(elems, elem_grids):
    grid_to_elems = defaultdict(list)

    for e, grids in elem_grids.items():
        for g in grids:
            grid_to_elems[g].append(e)

    adj = {e: set() for e in elems}

    for owners in grid_to_elems.values():
        if len(owners) > 1:
            for i in range(len(owners)):
                for j in range(i + 1, len(owners)):
                    a, b = owners[i], owners[j]
                    adj[a].add(b)
                    adj[b].add(a)

    return adj

def connected_components_T(adj, elems):
    visited = set()
    comps = []

    for e in elems:
        if e in visited:
            continue

        q = deque([e])
        comp = []
        visited.add(e)

        while q:
            u = q.popleft()
            comp.append(u)
            for v in adj[u]:
                if v not in visited:
                    visited.add(v)
                    q.append(v)

        comps.append(comp)

    return comps

def find_triplet_centers_for_group_T(comp, grid_to_elems, labels_map):
    comp_set = set(comp)
    centers = []

    for gid, owners in grid_to_elems.items():
        owners_in_comp = [e for e in owners if e in comp_set]
        if not owners_in_comp:
            continue

        cntA = cntB = cntT = cntC = 0
        for e in owners_in_comp:
            lbls = labels_map.get(e, set())
            if "A" in lbls: cntA += 1
            if "B" in lbls: cntB += 1
            if "T" in lbls: cntT += 1
            if "C" in lbls: cntC += 1

        if cntA == 1 and cntB == 1 and cntT == 1 and cntC == 0:
            centers.append(gid)

    return centers

def classify_and_assign_group_T(
    deck,
    comp,
    center_gid,
    grid_to_elems,
    labels_map,
    elem_grids,
    out_sets
):
    center_xyz = get_grid_coords_T(deck, center_gid)
    if center_xyz is None:
        print("  Skip Below Group for T Element Set : center node has no X1/X2/X3")
        return False

    owners_center = [e for e in grid_to_elems[center_gid] if e in comp]

    a_elem = next((e for e in owners_center if "A" in labels_map.get(e, set())), None)
    b_elem = next((e for e in owners_center if "B" in labels_map.get(e, set())), None)
    t_elem = next((e for e in owners_center if "T" in labels_map.get(e, set())), None)

    if not a_elem or not b_elem or not t_elem:
        print("  Skip Below Group for T Element Set : cannot resolve A/B/T shells at center")
        return False

    c_edge_gid = None
    c_elem = None

    for gid in elem_grids[t_elem]:
        if gid == center_gid:
            continue

        owners_n = [e for e in grid_to_elems.get(gid, []) if e in comp]
        if len(owners_n) != 2:
            continue

        if t_elem in owners_n:
            other = owners_n[0] if owners_n[1] == t_elem else owners_n[1]
            if "C" in labels_map.get(other, set()):
                c_edge_gid = gid
                c_elem = other
                break

    if c_edge_gid is None or c_elem is None:
        print("  Skip Below Group for T Element Set : no C-edge node (exactly t + C)")
        return False

    c_edge_xyz = get_grid_coords_T(deck, c_edge_gid)
    if c_edge_xyz is None:
        print("  Skip Below Group for T Element Set : C-edge node has no X1/X2/X3")
        return False
    a_corner_gid = None
    for gid in elem_grids[a_elem]:
        if gid == center_gid:
            continue

        owners_n = [e for e in grid_to_elems.get(gid, []) if e in comp]
        if len(owners_n) == 1 and owners_n[0] == a_elem:
            a_corner_gid = gid
            break

    if a_corner_gid is None:
        print("  Skip Below Group for T Element Set : no A-corner GRID (exactly one shell: Side_A)")
        return False

    a_corner_xyz = get_grid_coords_T(deck, a_corner_gid)
    if a_corner_xyz is None:
        print("  Skip Below Group for T Element Set : A-corner GRID has no X1/X2/X3")
        return False

    center_C_vec = v_norm_T(v_sub_T(c_edge_xyz, center_xyz))
    center_A_vec = v_norm_T(v_sub_T(a_corner_xyz, center_xyz))

    if center_C_vec is None or center_A_vec is None:
        print("  Skip Below Group for T Element Set : vectors undefined")
        return False

    n_T = normal_of_shell_T(t_elem)
    n_A = normal_of_shell_T(a_elem)
    n_B = normal_of_shell_T(b_elem)

    if n_T is None or n_A is None or n_B is None:
        print("  Skip Below Group for T Element Set : ANSA shell normals unavailable")
        return False

    same_C_vs_nA = (v_dot_T(center_C_vec, n_A) > EPS)
    same_A_vs_nT = (v_dot_T(center_A_vec, n_T) > EPS)
    same_A_vs_nB = (v_dot_T(n_A, n_B) > EPS)

    comp_A = [e for e in comp if "A" in labels_map.get(e, set())]
    comp_B = [e for e in comp if "B" in labels_map.get(e, set())]
    comp_T = [e for e in comp if "T" in labels_map.get(e, set())]

    if same_A_vs_nB:

        if same_C_vs_nA and same_A_vs_nT:
            base.AddToSet(out_sets["M203"], comp_A)
            base.AddToSet(out_sets["M204"], comp_B)
            base.AddToSet(out_sets["M205"], comp_T)

        elif same_C_vs_nA and (not same_A_vs_nT):
            base.AddToSet(out_sets["M201"], comp_A)
            base.AddToSet(out_sets["M202"], comp_B)
            base.AddToSet(out_sets["M205"], comp_T)

        elif (not same_C_vs_nA) and (not same_A_vs_nT):
            base.AddToSet(out_sets["M201"], comp_A)
            base.AddToSet(out_sets["M202"], comp_B)
            base.AddToSet(out_sets["M205"], comp_T)

        else:
            base.AddToSet(out_sets["M202"], comp_A)
            base.AddToSet(out_sets["M204"], comp_B)
            base.AddToSet(out_sets["M205"], comp_T)

    else:
        base.AddToSet(out_sets["M207"], comp_T)

        if same_C_vs_nA and same_A_vs_nT:
            base.AddToSet(out_sets["M201"], comp_A)
            base.AddToSet(out_sets["M204"], comp_B)

        elif same_C_vs_nA and (not same_A_vs_nT):
            base.AddToSet(out_sets["M201"], comp_A)
            base.AddToSet(out_sets["M202"], comp_B)

        elif (not same_C_vs_nA) and (not same_A_vs_nT):
            base.AddToSet(out_sets["M202"], comp_A)
            base.AddToSet(out_sets["M203"], comp_B)

        else:
            base.AddToSet(out_sets["M202"], comp_A)
            base.AddToSet(out_sets["M201"], comp_B)

    return True

def run_assignment(deck):

    union_shells, labels_map = build_union_and_labels(deck)
    if not union_shells:
        print("No visible shells found across the four sets.")
        return

    grid_to_elems, elem_grids = build_grid_to_elems(deck, union_shells)
    adj = build_adjacency_any_grid(union_shells, elem_grids)
    comps = connected_components(adj, union_shells)

    out_sets = {
        name: get_or_create_global_set(deck, name, OUT_SETS[name])
        for name in OUT_SETS
    }

    for i, comp in enumerate(comps, start=1):
        ids = [e._id for e in comp]

        centers = find_triplet_centers_for_group(
            comp,
            grid_to_elems,
            labels_map
        )

        if not centers:
            print("  Skip Below Group for T Element Set : no centers node found")
            print(f"  Critical Element Group [{i}] ({ids})")
            continue

        center_gid = centers[0]

        ok = classify_and_assign_group(
            deck,
            comp,
            center_gid,
            grid_to_elems,
            labels_map,
            elem_grids,
            out_sets
        )

        if not ok:
            print(f"Critical Element Group [{i}] ({ids})")

def get_shell_nodes(deck, elem):
    keys = ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8")
    vals = base.GetEntityCardValues(deck, elem, keys)
    return [vals[k] for k in keys if k in vals and vals[k]]


def build_node_cache(deck, elems):
    elem_nodes = {}
    elem_nodes_set = {}

    for e in elems:
        nodes = get_shell_nodes(deck, e)
        elem_nodes[e] = nodes
        elem_nodes_set[e] = set(nodes)

    return elem_nodes, elem_nodes_set


def shared_node_count(e1, e2, elem_nodes_set):
    return len(elem_nodes_set[e1].intersection(elem_nodes_set[e2]))


def build_adjacency_any_node(elems, elem_nodes):
    node_to_elems = defaultdict(list)

    for e, nodes in elem_nodes.items():
        for n in nodes:
            node_to_elems[n].append(e)

    adj = {e: set() for e in elems}

    for owners in node_to_elems.values():
        if len(owners) > 1:
            for i in range(len(owners)):
                for j in range(i + 1, len(owners)):
                    a, b = owners[i], owners[j]
                    adj[a].add(b)
                    adj[b].add(a)

    return adj

def build_edge_adjacency(elems, elem_nodes):
    node_to_elems = defaultdict(list)

    for e, nodes in elem_nodes.items():
        for n in nodes:
            node_to_elems[n].append(e)

    pair_count = defaultdict(int)

    for owners in node_to_elems.values():
        for i in range(len(owners)):
            for j in range(i + 1, len(owners)):
                a, b = owners[i], owners[j]
                key = (a, b) if id(a) < id(b) else (b, a)
                pair_count[key] += 1

    adj_edge = {e: set() for e in elems}

    for (a, b), cnt in pair_count.items():
        if cnt >= 2:
            adj_edge[a].add(b)
            adj_edge[b].add(a)

    return adj_edge


def connected_components(adj_any, elems):
    visited = set()
    comps = []

    for e in elems:
        if e in visited:
            continue

        q = deque([e])
        comp = []
        visited.add(e)

        while q:
            u = q.popleft()
            comp.append(u)
            for v in adj_any[u]:
                if v not in visited:
                    visited.add(v)
                    q.append(v)

        comps.append(comp)

    return comps


def pick_corner_elements(comp, adj_edge):
    corners = [
        e for e in comp
        if len(adj_edge[e].intersection(comp)) == 2
    ]
    return corners


def walk_side_from_corner(corner, adj_edge, elem_nodes_set):
    neighbors = list(adj_edge[corner])

    if len(neighbors) < 1:
        return [corner]

    candidates = []

    first_choices = neighbors if len(neighbors) == 2 else [neighbors[0]]

    for first in first_choices:
        ok_choice = False

        for nn in adj_edge[first]:
            if nn == corner:
                continue

            if shared_node_count(nn, corner, elem_nodes_set) == 0:
                ok_choice = True
                break

        if not ok_choice:
            pass
        
            path = [corner, first]
    prev = corner
    cur = first

    while True:
        nexts = [n for n in adj_edge[cur] if n != prev]
        nexts = [
            n for n in nexts
            if shared_node_count(n, prev, elem_nodes_set) == 0
        ]

        if not nexts:
            break

        nxt = nexts[0]
        path.append(nxt)
        prev, cur = cur, nxt

    candidates.append(path)

    if not candidates:
        return [corner]

    return max(candidates, key=len)


def extract_side_1_for_component(comp, adj_edge, elem_nodes_set):
    corners = pick_corner_elements(comp, adj_edge)

    if corners:
        side1 = walk_side_from_corner(
            corners[0],
            adj_edge,
            elem_nodes_set
        )
    else:
        start = sorted(comp, key=lambda e: e._id)[0]
        side1 = walk_side_from_corner(
            start,
            adj_edge,
            elem_nodes_set
        )

    return side1


def create_global_sets_for_double_chains(deck, set_name):
    shells = base.CollectEntities(
        deck,
        None,
        "SHELL",
        filter_visible=True
    )

    if not shells:
        print("No visible SHELL elements found.")
        return None, None

    elem_nodes, elem_nodes_set = build_node_cache(deck, shells)
    adj_any = build_adjacency_any_node(shells, elem_nodes)
    adj_edge = build_edge_adjacency(shells, elem_nodes)

    comps = connected_components(adj_any, shells)

    set1 = base.CreateEntity(deck, "SET", {"Name": f"{set_name}_Side_A"})
    set2 = base.CreateEntity(deck, "SET", {"Name": f"{set_name}_Side_B"})

    total_s1 = 0
    total_s2 = 0

    for i, comp in enumerate(comps, start=1):
        sub_adj_edge = {
            e: adj_edge[e].intersection(comp)
            for e in comp
        }

        side1 = extract_side_1_for_component(
            comp,
            sub_adj_edge,
            elem_nodes_set
        )

        side1_set = set(side1)
        side2 = [e for e in comp if e not in side1_set]

        if side1:
            base.AddToSet(set1, side1)
        if side2:
            base.AddToSet(set2, side2)

        total_s1 += len(side1)
        total_s2 += len(side2)

    return set1, set2

def get_set_by_name(deck, name):
    for s in base.CollectEntities(deck, None, "SET"):
        card = base.GetEntityCardValues(deck, s, ("Name",))
        if card and card.get("Name") == name:
            return s
    return None


def collect_visible_shells(deck, container_entity=None):
    return base.CollectEntities(
        deck,
        container_entity,
        "SHELL",
        filter_visible=True,
        recursive=True
    )


def cache_nodes(deck, elems):
    elem_nodes = {}
    elem_nodes_set = {}

    keys = ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8")

    for e in elems:
        vals = base.GetEntityCardValues(deck, e, keys)
        nodes = [vals[k] for k in keys if k in vals and vals[k]]
        elem_nodes[e] = nodes
        elem_nodes_set[e] = set(nodes)

    return elem_nodes, elem_nodes_set


def shares_at_least_two_nodes(e, others, elem_nodes_set):
    e_nodes = elem_nodes_set[e]
    for o in others:
        if len(e_nodes.intersection(elem_nodes_set[o])) >= 2:
            return True
    return False


def build_T_joint_side_C(
    deck,
    name_T="T_Joint_delt",
    name_A="T_Joint_delt_Side_A",
    name_B="T_Joint_delt_Side_B",
    name_out="T_Joint_delt_Side_C",
    delete_existing=True
):
    set_T = get_set_by_name(deck, name_T)
    set_A = get_set_by_name(deck, name_A)
    set_B = get_set_by_name(deck, name_B)

    if not set_T:
        raise ValueError(f"SET '{name_T}' not found.")
    if not set_A:
        raise ValueError(f"SET '{name_A}' not found.")
    if not set_B:
        raise ValueError(f"SET '{name_B}' not found.")

    shells_T = collect_visible_shells(deck, set_T)
    shells_A = collect_visible_shells(deck, set_A)
    shells_B = collect_visible_shells(deck, set_B)
    all_visible_shells = collect_visible_shells(deck, None)

    nodes_T, nodes_T_set = cache_nodes(deck, shells_T)
    nodes_A, nodes_A_set = cache_nodes(deck, shells_A)
    nodes_B, nodes_B_set = cache_nodes(deck, shells_B)
    nodes_all, nodes_all_set = cache_nodes(deck, all_visible_shells)

    in_T = set(shells_T)
    in_A = set(shells_A)
    in_B = set(shells_B)

    exclude = in_T | in_A | in_B

    candidates = [
        e for e in all_visible_shells
        if e not in exclude
    ]

    side_C = []

    for e in candidates:
        shares_T = shares_at_least_two_nodes(e, shells_T, nodes_all)
        if not shares_T:
            continue

        shares_A = shares_at_least_two_nodes(e, shells_A, nodes_all)
        shares_B = shares_at_least_two_nodes(e, shells_B, nodes_all)

        if not shares_A and not shares_B:
            side_C.append(e)


    if delete_existing:
        old = get_set_by_name(deck, name_out)
        if old:
            base.DeleteEntity(old)

    set_C = base.CreateEntity(deck, "SET", {"Name": name_out})
    if side_C:
        base.AddToSet(set_C, side_C)

    return set_C, side_C


def get_elements_from_set(set_name):
    deck = constants.NASTRAN
    sets = base.CollectEntities(deck, None, "SET")
    target_set = None
    for s in sets:
        vals = base.GetEntityCardValues(deck, s, ("Name",))
        if vals and vals.get("Name") == set_name:
            target_set = s
            break
    if not target_set:
        print(f"SET '{set_name}' not found.")
        return []
    elems = base.CollectEntities(deck, target_set, "SHELL", recursive=True)
    if elems:
        base.Or(elems)
        base.Highlight("on")
        triple_check = base.Checks.GetViolations()
        triple_reports = triple_check.GetReport(
            "ncs_soln:Check_ERC_NASTRAN_Triple_Joint"
        )
        triple_joint_elems = set()
        for report in triple_reports:
            for issue in report.Issues:
                for ent in issue.Entities:
                    triple_joint_elems.add(ent)
        base.Or(triple_joint_elems)
        base.Highlight("off")
    
        create_global_sets_for_double_chains(deck, set_name)
        build_T_joint_side_C(
            deck,
            name_T="T_Joint_delt",
            name_A="T_Joint_delt_Side_A",
            name_B="T_Joint_delt_Side_B",
            name_out="T_Joint_delt_Side_C",
            delete_existing=True
        )
        return elems
    
def t_node():
    deck = constants.NASTRAN

    def get_shell_node_ids(shell):
        keys = ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8")
        vals = base.GetEntityCardValues(deck, shell, keys)
        return [
            vals[k] for k in keys
            if k in vals and vals[k] and vals[k] != 0
        ]

    shells = base.CollectEntities(
        deck,
        None,
        "SHELL",
        filter_visible=True
    ) or []

    shell_nodes = {}
    node_to_shells = {}

    for shell in shells:
        nodes = get_shell_node_ids(shell)
        shell_nodes[shell._id] = nodes
        for n in nodes:
            node_to_shells.setdefault(n, []).append(shell._id)

    visited = set()
    groups = []

    for sid in shell_nodes:
        if sid not in visited:
            stack = [sid]
            group = []

            while stack:
                current = stack.pop()
                if current in visited:
                    continue

                visited.add(current)
                group.append(current)

                for node in shell_nodes[current]:
                    for neighbor in node_to_shells.get(node, []):
                        if neighbor not in visited:
                            stack.append(neighbor)

            groups.append(group)

    base.Neighb("1")

    triple_check = base.Checks.mesh.TripleBounds()
    triple_reports = triple_check.execute(
        exec_mode=base.Check.EXEC_ON_VS,
        report=base.Check.REPORT_NONE
    )

    node_usage = {}

    for report in triple_reports:
        for issue in report.Issues:
            for ent in issue.Entities:
                vals = base.GetEntityCardValues(
                    deck,
                    ent,
                    ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8")
                )
                nodes_issue = [
                    vals[k] for k in vals
                    if vals[k] and vals[k] != 0
                ]

                for n in nodes_issue:
                    node_usage[n] = node_usage.get(n, 0) + 1

    triple_node_list = [
        nid for nid, count in node_usage.items()
        if count >= 3
    ]

    set1 = []
    set2 = []
    set3 = []

    used_nodes = set()

    for i, group in enumerate(groups, start=1):
        neighbor_map = {sid: set() for sid in group}

        for sid in group:
            for node in shell_nodes[sid]:
                for neighbor in node_to_shells.get(node, []):
                    if neighbor in group and neighbor != sid:
                        neighbor_map[sid].add(neighbor)

        outer = [
            sid for sid, neighbors in neighbor_map.items()
            if len(neighbors) == 1
        ]

        if len(outer) < 2:
            continue

        first_outer, second_outer = outer[0], outer[1]

    first_nodes = shell_nodes[first_outer]
    shared_first = [
        n for n in first_nodes
        for nb in neighbor_map[first_outer]
        if n in shell_nodes[nb]
    ]
    free_first = [
        n for n in first_nodes
        if n not in shared_first and n in triple_node_list
    ]

    second_nodes = shell_nodes[second_outer]
    shared_second = [
        n for n in second_nodes
        for nb in neighbor_map[second_outer]
        if n in shell_nodes[nb]
    ]
    free_second = [
        n for n in second_nodes
        if n not in shared_second and n in triple_node_list
    ]

    if free_first:
        node_ent = base.GetEntity(deck, "GRID", free_first[0])
        if node_ent:
            set1.append(node_ent)
            used_nodes.add(free_first[0])

    if free_second:
        node_ent = base.GetEntity(deck, "GRID", free_second[0])
        if node_ent:
            set2.append(node_ent)
            used_nodes.add(free_second[0])

    remaining_nodes = [
        n for n in triple_node_list
        if n not in used_nodes
    ]

    for nid in remaining_nodes:
        node_ent = base.GetEntity(deck, "GRID", nid)
        if node_ent:
            set3.append(node_ent)

    return set1, set2, set3


def lap_node():
    deck = constants.NASTRAN
    shells = base.CollectEntities(deck, None, "SHELL", filter_visible=True)
    node_to_shells = {}
    shell_nodes = {}

    for shell in shells:
        vals = base.GetEntityCardValues(deck, shell, ("G1", "G2", "G3", "G4"))
        nodes = [vals["G1"], vals["G2"], vals["G3"], vals["G4"]]
        shell_nodes[shell._id] = nodes
        for n in nodes:
            node_to_shells.setdefault(n, []).append(shell._id)

    visited = set()
    groups = []

    for shell_id in shell_nodes:
        if shell_id not in visited:
            stack = [shell_id]
            group = []

            while stack:
                current = stack.pop()
                if current in visited:
                    continue

                visited.add(current)
                group.append(current)

                for node in shell_nodes[current]:
                    for neighbor in node_to_shells.get(node, []):
                        if neighbor not in visited:
                            stack.append(neighbor)

            groups.append(group)

    set1 = []
    set2 = []
    set3 = []
    excluded_nodes = set()
    all_nodes_from_shells = set()

    for i, group in enumerate(groups, start=1):
        neighbor_map = {sid: set() for sid in group}

        for sid in group:
            for node in shell_nodes[sid]:
                for neighbor in node_to_shells[node]:
                    if neighbor in group and neighbor != sid:
                        neighbor_map[sid].add(neighbor)

        outer = [
            sid for sid, neighbors in neighbor_map.items()
            if len(neighbors) == 1
        ]

        if len(outer) < 2:
            continue

        first_outer, second_outer = outer[0], outer[1]

        for sid in group:
            all_nodes_from_shells.update(shell_nodes[sid])

        first_nodes = shell_nodes[first_outer]
        shared_first = [
            n for n in first_nodes
            for nb in neighbor_map[first_outer]
            if n in shell_nodes[nb]
        ]
        free_first = [
            n for n in first_nodes
            if n not in shared_first
        ]

        second_nodes = shell_nodes[second_outer]
        shared_second = [
            n for n in second_nodes
            for nb in neighbor_map[second_outer]
            if n in shell_nodes[nb]
        ]
        free_second = [
            n for n in second_nodes
            if n not in shared_second
        ]

        for nid in free_first:
            node_ent = base.GetEntity(deck, "GRID", nid)
            set1.append(node_ent)
            excluded_nodes.add(nid)

        for nid in free_second:
            node_ent = base.GetEntity(deck, "GRID", nid)
            set2.append(node_ent)
            excluded_nodes.add(nid)

    remaining_nodes = all_nodes_from_shells - excluded_nodes

    for nid in remaining_nodes:
        node_ent = base.GetEntity(deck, "GRID", nid)
        set3.append(node_ent)

    return set1, set2, set3


def angle_between_shells(shell1, shell2):
    n1 = base.GetNormalVectorOfShell(shell1)
    n2 = base.GetNormalVectorOfShell(shell2)
    dot = sum(a * b for a, b in zip(n1, n2))

    if dot > 1:
        dot = round(dot)
    if dot < -1:
        dot = round(dot)

    mag1 = round(math.sqrt(sum(x * x for x in n1)))
    mag2 = round(math.sqrt(sum(x * x for x in n2)))

    return math.degrees(math.acos(dot / (mag1 * mag2)))


def get_shell_nodes(deck, elem):
    keys = ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8")
    vals = base.GetEntityCardValues(deck, elem, keys)
    return [vals[k] for k in keys if k in vals and vals[k]]

def build_adjacency_any_node(deck, elems, elem_nodes=None):
    if elem_nodes is None:
        elem_nodes = {}
        for e in elems:
            elem_nodes[e] = get_shell_nodes(deck, e)

    node_to_elems = defaultdict(list)
    for e, nodes in elem_nodes.items():
        for n in nodes:
            node_to_elems[n].append(e)

    adj = {e: set() for e in elems}
    for owners in node_to_elems.values():
        if len(owners) > 1:
            for i in range(len(owners)):
                for j in range(i + 1, len(owners)):
                    a, b = owners[i], owners[j]
                    adj[a].add(b)
                    adj[b].add(a)

    return adj, elem_nodes


def is_loop(adj, group):
    return all(len(adj[e]) == 2 for e in group)


def find_endpoints(adj, group):
    return [e for e in group if len(adj[e]) == 1]


def order_chain_from_endpoint(adj, start):
    order = []
    visited = set()
    cur = start
    prev = None

    while cur is not None:
        order.append(cur)
        visited.add(cur)
        next_candidates = [
            n for n in adj[cur]
            if n != prev and n not in visited
        ]

        if not next_candidates:
            next_candidates = [
                n for n in adj[cur]
                if n not in visited
            ]

        prev, cur = cur, (
            next_candidates[0] if next_candidates else None
        )

    return order


def order_loop(adj, group):
    start = group[0]
    order = [start]
    visited = {start}
    prev = None
    cur = start

    while True:
        next_candidates = [n for n in adj[cur] if n != prev]
        next_unvisited = [
            n for n in next_candidates
            if n not in visited
        ]

        nxt = (
            next_unvisited[0]
            if next_unvisited
            else (
                next_candidates[0]
                if next_candidates else None
            )
        )

        if nxt is None or nxt == start:
            break

        order.append(nxt)
        visited.add(nxt)
        prev, cur = cur, nxt

        if len(order) == len(group):
            break

    if len(order) < len(group):
        remaining = set(group) - set(order)
        for r in list(remaining):
            nbrs = adj[r]
            pos = None
            for i, e in enumerate(order):
                if e in nbrs:
                    pos = i + 1
                    break
            if pos is None:
                order.append(r)
            else:
                order.insert(pos, r)

    return order

def longest_path_order(adj, group):
    def bfs(src):
        pred = {src: None}
        q = deque([src])

        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in pred:
                    pred[v] = u
                    q.append(v)

        far = u
        return pred, far

    start = group[0]
    pred1, A = bfs(start)
    pred2, B = bfs(A)

    path = []
    cur = B
    while cur is not None:
        path.append(cur)
        cur = pred2[cur]

    path = list(reversed(path))
    ordered = list(path)
    in_order = set(ordered)

    remaining = deque([e for e in group if e not in in_order])
    while remaining:
        e = remaining.popleft()
        attachment_points = [
            i for i, x in enumerate(ordered)
            if x in adj[e]
        ]

        if attachment_points:
            ordered.insert(attachment_points[0] + 1, e)
            in_order.add(e)
        else:
            remaining.append(e)
            if all(x in in_order for x in group):
                break

        if len(remaining) == 1 and remaining[0] == e:
            ordered.append(e)
            in_order.add(e)
            remaining.clear()

    return ordered


def order_group(adj, group):
    degs = {e: len(adj[e]) for e in group}
    endpoints = [e for e, d in degs.items() if d == 1]

    if endpoints:
        return order_chain_from_endpoint(adj, endpoints[0])
    elif is_loop(adj, group):
        return order_loop(adj, group)
    else:
        return longest_path_order(adj, group)
    
def group_connected_shells(deck, elems):
    solid_elems = elems
    if not solid_elems:
        return []

    adj, elem_nodes = build_adjacency(deck, solid_elems)
    visited = set()
    components = []

    for e in solid_elems:
        if e in visited:
            continue
        q = deque([e])
        comp = []
        visited.add(e)

        while q:
            u = q.popleft()
            comp.append(u)
            for v in adj[u]:
                if v not in visited:
                    visited.add(v)
                    q.append(v)

        components.append(comp)

    ordered_groups = []
    for comp in components:
        sub_adj = {e: adj[e].intersection(comp) for e in comp}
        ordered = order_group(sub_adj, comp)
        ordered_groups.append(ordered)

    return ordered_groups


def classify_groups(deck, solid_elems, triple_joint_elems, group):
    side_joint_set = base.CreateEntity(deck, "SET", {"Name": "T_Joint_side"})
    t_joint_set = base.CreateEntity(deck, "SET", {"Name": "T_Joint_center"})
    critical_groups = []

    for idx, elems in enumerate(group, start=1):
        if len(elems) < 3:
            continue

        mid_index = len(elems) // 2
        second_elem = elems[mid_index]
        conn = base.GetEntityCardValues(
            deck,
            second_elem,
            ("G1", "G2", "G3", "G4")
        )
        nodes = [conn["G1"], conn["G2"], conn["G3"], conn["G4"]]
        node_entities = [
            base.GetEntity(deck, "GRID", n)
            for n in nodes if n
        ]

        shell_refs = [
            e for e in base.AdvancedEntityRelations(deck)
            if e.get("ENTITY") == "SHELL"
            for node in node_entities
        ]

        vis_elems = base.CollectEntities(
            deck, None, "SHELL", filter_visible=True
        )

        node_to_shells = {}
        for shell in vis_elems:
            conn = base.GetEntityCardValues(
                deck,
                shell,
                ("G1", "G2", "G3", "G4")
            )
            for key, nid in conn.items():
                if nid and nid in nodes:
                    node_to_shells.setdefault(nid, []).append(shell)

        node_refs = []
        for node_id in nodes:
            refs = node_to_shells.get(node_id, [])
            node_refs.append(refs)

        four_nodes = [i for i, refs in enumerate(node_refs) if len(refs) == 4]
        six_nodes = [i for i, refs in enumerate(node_refs) if len(refs) == 6]

        if len(four_nodes) == 2 and len(six_nodes) == 2:
            common_first_two = set(node_refs[four_nodes[0]]) & set(node_refs[four_nodes[1]])
            common_first_two = [
                e for e in common_first_two
                if e not in solid_elems and e not in triple_joint_elems
            ]

            short_elem_1 = common_first_two[0] if common_first_two else None

            common_last_two = set(node_refs[six_nodes[0]]) & set(node_refs[six_nodes[1]])
            common_last_two = [
                e for e in common_last_two
                if e in triple_joint_elems and e not in solid_elems
            ]

            short_elem_2 = common_last_two[0] if len(common_last_two) == 1 else None

            if short_elem_1 and short_elem_2:
                angle_short = angle_between_shells(short_elem_1, short_elem_2)
                angle_main = angle_between_shells(second_elem, short_elem_1)
                angle_sec = angle_between_shells(second_elem, short_elem_2)

                if abs(angle_short) < 5 or abs(angle_short - 180) < 5:
                    if abs(angle_main) < 5 or abs(angle_main - 180) < 5:
                        base.AddToSet(side_joint_set, elems)
                    elif abs(angle_sec) < 5 or abs(angle_sec - 180) < 5:
                        base.AddToSet(t_joint_set, elems)
                    elif abs(angle_main - 90) < 5 or abs(angle_sec - 90) < 5:
                        base.AddToSet(t_joint_set, elems)
                    else:
                        print(
                            "In below group : more and lower elements are neither parallel nor perpendicular "
                            "and is crossed angle tolerance limit"
                        )
                        critical_groups[idx] = elems
                        print(
                            "Critical weld group {} ({}-id for e in elems)".format(idx)
                        )
                else:
                    print(
                        "In below group : more two elements is not parallel and angle between them is more than 5 degree"
                    )
                    critical_groups[idx] = elems
                    print(
                        "Critical weld group {} ({}-id for e in elems)".format(idx)
                    )
            else:
                print("In below group : elements are perpendicular combinations")
                critical_groups[idx] = elems
                print(
                    "Critical weld group {} ({}-id for e in elems)".format(idx)
                )
        else:
            print("In below group : there are nonstandard combinations")
            critical_groups[idx] = elems
            print(
                "Critical weld group {} ({}-id for e in elems)".format(idx)
            )

        tjb_elems = base.CollectEntities(deck, t_joint_set, "SHELL", recursive=True)
        base.Or(tjb_elems)
        start_l,end_l,middel_l=lap_node()

        tjs_elems = base.CollectEntities(deck, side_joint_set, "SHELL", recursive=True)
        base.Or(tjs_elems)
        start_l,end_l,middel_l=t_node()

        start2_start_3()
        extend_joint_s()
        solid_model_validate_t()

        set1 = base.CreateEntity(deck, "SET", {"Name": "Core_side", "ID": 301})
        base.AddToSet(set1, start_s)

        set2 = base.CreateEntity(deck, "SET", {"Name": "Core_end", "ID": 302})
        base.AddToSet(set2, end_s)

        set3 = base.CreateEntity(deck, "SET", {"Name": "Core_mid", "ID": 303})
        base.AddToSet(set3, mid_s)

        return critical_groups

def create_set_for_material(deck, material_name, new_set_name):
    material_id = None
    for mat in base.CollectEntities(deck, None, "MATERIAL"):
        vals = base.GetEntityCardValues(deck, mat, ("Name",))
        if vals.get("Name") == material_name:
            material_id = mat
            break

    if not material_id:
        print(f"Material '{material_name}' not found in the model.")
        return None

    elems = base.CollectEntities(deck, material_id, "SHELL", recursive=True)
    if not elems:
        print(f"No shell elements found for material '{material_name}'.")
        return None

    new_set = base.CreateEntity(deck, "SET", {"Name": new_set_name})
    base.AddToSet(new_set, elems)
    return new_set


def main():
    deck = constants.NASTRAN
    material_name = "SHELL_MAT"
    set_name = "weld_elements"

    create_set_for_material(deck, material_name, set_name)

    sets = base.CollectEntities(deck, None, "SET")

    target_set = None
    for s in sets:
        vals = base.GetEntityCardValues(deck, s, ("Name",))
        if vals.get("Name") == set_name:
            target_set = s
            break

    if not target_set:
        print(f"SET '{set_name}' not found.")
        return

    weld_elems = base.CollectEntities(deck, target_set, "SHELL", recursive=True)
    base.Or(weld_elems)

    groups = group_connected_shells(deck, weld_elems)
    print(f"Total weld groups are {len(groups)}")

    base.Neighb("1")

    triple_check = base.Checks.mesh.TripleBounds()
    triple_reports = triple_check.execute(
        exec_mode=base.Check.EXEC_ON_V15,
        report=base.Check.REPORT_NONE
    )

    triple_bound_elems = set()
    for report in triple_reports:
        for issue in report.issues:
            for ent in issue.entities:
                triple_bound_elems.add(ent)

    critical = classify_groups(deck, weld_elems, triple_bound_elems, groups)
    if critical:
        print("Critical Groups:")
        for gid, elems in critical.items():
            print(f"Group {gid} ({[e._id for e in elems]})")
    else:
        print("No Critical Groups are Present")

    elements_L = get_elements_from_set("Lap_joint_deck")  #### Require set
    elements_T = get_elements_from_set("T_joint_deck")    #### Require set

    base.All()
    if elements_T:
        run_assignment(deck)

    base.All()
    if elements_L:
        run_lap_assignment(deck)


if __name__ == "__main__":
    main()
