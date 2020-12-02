
def support_map_vectorized1(linked,num_indirect_equal_direct=3):
    # columns
    # 'team_j', 'team_i_name', 'team_i_score', 'team_i_H_A_N',
    # 'team_j_i_score', 'team_j_i_H_A_N', 'game_i_j', 'team_k_name',
    # 'team_k_score', 'team_k_H_A_N', 'team_j_k_score', 'team_j_k_H_A_N',
    # 'game_k_j'
    linked["direct"] = linked["team_i_name"] == linked["team_k_name"]
    # | (linked["team_i_name"] == linked["team_j_k_name"]) | (linked["team_k_name"] == linked["team_j_k_name"])
    for_index1 = linked[["team_i_name","team_k_name"]].copy()
    for_index1.loc[linked["direct"]] = linked.loc[linked["direct"],["team_i_name","team_j_name"]]
    for_index1.columns = ["team1","team2"]
    for_index2 = linked[["team_k_name","team_i_name"]].copy()
    for_index2.loc[linked["direct"]] = linked.loc[linked["direct"],["team_j_name","team_i_name"]]
    for_index2.columns = ["team1","team2"]
    index_ik = pd.MultiIndex.from_frame(for_index1,sortorder=0)
    index_ki = pd.MultiIndex.from_frame(for_index2,sortorder=0)
    
    #######################################
    # part to modify
    # direct
    d_ik = linked['team_i_score'] - linked['team_j_i_score']
    direct_thres = 1
    support_ik = num_indirect_equal_direct*(linked["direct"] & (d_ik > direct_thres)).astype(int)
    support_ki = num_indirect_equal_direct*(linked["direct"] & (d_ik < -direct_thres)).astype(int)

    # indirect
    d_ij = linked["team_i_score"] - linked["team_j_i_score"]
    d_kj = linked["team_k_score"] - linked["team_j_k_score"]
    
    # always a positive and it captures that if i beat j by 5 points and k beat j by 2 points then this spread is 3
    spread = np.abs(d_ij - d_kj) 
    
    support_ik += ((~linked["direct"]) & (d_ij > 0) & (d_kj > 0) & (d_ij > d_kj) & (spread > 10)).astype(int)
    support_ik += ((~linked["direct"]) & (d_ij < 0) & (d_kj < 0) & (d_ij > d_kj) & (spread > 15)).astype(int)
    support_ik += ((~linked["direct"]) & (d_ij > 0) & (d_kj < 0) & (spread > 2)).astype(int)
    
    support_ki += ((~linked["direct"]) & (d_kj > 0) & (d_ij > 0) & (d_kj > d_ij) & (spread > 10)).astype(int)
    support_ki += ((~linked["direct"]) & (d_kj < 0) & (d_ij < 0) & (d_kj > d_ij) & (spread > 15)).astype(int)
    support_ki += ((~linked["direct"]) & (d_kj > 0) & (d_ij < 0) & (spread > 2)).astype(int)
    
    # end part to modify
    #######################################    
    linked["support_ik"]=support_ik
    linked["index_ik"]=index_ik
    linked["support_ki"]=support_ki
    linked["index_ki"]=index_ki
        
    #prepare_ret = linked.drop_duplicates(subset='games', keep='first')[["index_ik","index_ki","support_ik","support_ki"]]
    ret1 = linked.set_index(index_ik)["support_ik"]
    ret2 = linked.set_index(index_ki)["support_ki"]
    ret = ret1.append(ret2)
    ret = ret.groupby(level=[0,1]).sum()

    return ret



def support_map_vectorized_direct(linked,direct_thres=1):
    # columns
    # 'team_j', 'team_i_name', 'team_i_score', 'team_i_H_A_N',
    # 'team_j_i_score', 'team_j_i_H_A_N', 'game_i_j', 'team_k_name',
    # 'team_k_score', 'team_k_H_A_N', 'team_j_k_score', 'team_j_k_H_A_N',
    # 'game_k_j'
    linked["direct"] = linked["team_i_name"] == linked["team_k_name"]
    linked = linked.loc[linked["direct"]].copy()
    # | (linked["team_i_name"] == linked["team_j_k_name"]) | (linked["team_k_name"] == linked["team_j_k_name"])
    for_index1 = linked[["team_i_name","team_k_name"]].copy()
    for_index1.loc[linked["direct"]] = linked.loc[linked["direct"],["team_i_name","team_j_name"]]
    for_index1.columns = ["team1","team2"]
    for_index2 = linked[["team_k_name","team_i_name"]].copy()
    for_index2.loc[linked["direct"]] = linked.loc[linked["direct"],["team_j_name","team_i_name"]]
    for_index2.columns = ["team1","team2"]
    index_ik = pd.MultiIndex.from_frame(for_index1,sortorder=0)
    index_ki = pd.MultiIndex.from_frame(for_index2,sortorder=0)
    
    #######################################
    # part to modify
    # direct
    d_ik = linked['team_i_score'] - linked['team_j_i_score']
    support_ik = (linked["direct"] & (d_ik > direct_thres)).astype(int)
    support_ki = (linked["direct"] & (d_ik < -direct_thres)).astype(int)
    
    # end part to modify
    #######################################    
    linked["support_ik"]=support_ik
    linked["index_ik"]=index_ik
    linked["support_ki"]=support_ki
    linked["index_ki"]=index_ki
    
    #prepare_ret = linked.drop_duplicates(subset='games', keep='first')[["index_ik","index_ki","support_ik","support_ki"]]
    ret1 = linked.set_index(index_ik)["support_ik"]
    ret2 = linked.set_index(index_ki)["support_ki"]
    ret = ret1.append(ret2)
    ret = ret.groupby(level=[0,1]).sum()

    return ret


def support_map_vectorized_direct_indirect_weighted(linked,direct_thres=1,spread_thres=0,weight_indirect=0.5,verbose=False):
    # columns
    # 'team_j', 'team_i_name', 'team_i_score', 'team_i_H_A_N',
    # 'team_j_i_score', 'team_j_i_H_A_N', 'game_i_j', 'team_k_name',
    # 'team_k_score', 'team_k_H_A_N', 'team_j_k_score', 'team_j_k_H_A_N',
    # 'game_k_j'
    linked["direct"] = linked["team_i_name"] == linked["team_k_name"]
    # | (linked["team_i_name"] == linked["team_j_k_name"]) | (linked["team_k_name"] == linked["team_j_k_name"])
    for_index1 = linked[["team_i_name","team_k_name"]].copy()
    for_index1.loc[linked["direct"]] = linked.loc[linked["direct"],["team_i_name","team_j_name"]]
    for_index1.columns = ["team1","team2"]
    for_index2 = linked[["team_k_name","team_i_name"]].copy()
    for_index2.loc[linked["direct"]] = linked.loc[linked["direct"],["team_j_name","team_i_name"]]
    for_index2.columns = ["team1","team2"]
    index_ik = pd.MultiIndex.from_frame(for_index1,sortorder=0)
    index_ki = pd.MultiIndex.from_frame(for_index2,sortorder=0)
    
    #######################################
    # part to modify
    # direct
    d_ik = linked['team_i_score'] - linked['team_j_i_score']
    support_ik = (linked["direct"] & (d_ik > direct_thres)).astype(int)
    support_ki = (linked["direct"] & (d_ik < -direct_thres)).astype(int)

    # indirect
    d_ij = linked["team_i_score"] - linked["team_j_i_score"]
    d_kj = linked["team_k_score"] - linked["team_j_k_score"]
    
    # always a positive and it captures that if i beat j by 5 points and k beat j by 2 points then this spread is 3
    spread = np.abs(d_ij - d_kj) 
    
    support_ik += weight_indirect*((~linked["direct"]) & (d_ij > 0) & (d_kj < 0) & (spread > spread_thres)).astype(int)
    
    support_ki += weight_indirect*((~linked["direct"]) & (d_kj > 0) & (d_ij < 0) & (spread > spread_thres)).astype(int)
    
    # end part to modify
    #######################################    
    linked["support_ik"]=support_ik
    linked["index_ik"]=index_ik
    linked["support_ki"]=support_ki
    linked["index_ki"]=index_ki
        
    if verbose:
        print('Direct')
        print("Total:",sum(linked["direct"] & (linked["support_ik"]>0)) + sum(linked["direct"] & (linked["support_ki"]>0)),
              "ik:",sum(linked["direct"] & (linked["support_ik"]>0)), 
              "ki:",sum(linked["direct"] & (linked["support_ki"]>0)))
        print('Indirect')
        print("Total:",sum((~linked["direct"]) & (linked["support_ik"]>0)) + sum(~linked["direct"] & (linked["support_ki"]>0)),
              "ik:",sum((~linked["direct"]) & (linked["support_ik"]>0)), 
              "ki:",sum(~linked["direct"] & (linked["support_ki"]>0)))
    
    #indices_ik = linked.index[(linked["support_ik"] > linked["support_ki"]) & ~linked['direct']]    
    #indices_ki = linked.index[(linked["support_ik"] > linked["support_ki"]) & ~linked['direct']] 
    #linked.loc[~linked['direct']] = 0
    #linked.loc[indices_ik] = 0.5*(linked.loc[indices_ik]["support_ik"] - linked.loc[indices_ik]["support_ki"])
    #linked.loc[indices_ik] = 0.5*(linked.loc[indices_ik]["support_ik"] - linked.loc[indices_ik]["support_ki"])
    
    ret1 = linked.set_index(index_ik)["support_ik"]
    ret2 = linked.set_index(index_ki)["support_ki"]
    ret = ret1.append(ret2)
    ret = ret.groupby(level=[0,1]).sum()
    return ret

