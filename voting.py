import numpy

CAND = 0
SCORE = 1
PLACE = 2

def ranked_choice_voting(candidate_rankings, voters, candidates):

    active_candidates = set(range(1, candidates + 1))
    elimination_order = []
    
    while len(active_candidates) > 1:
        first_choice_votes = {candidate: 0 for candidate in active_candidates}
        for voter in candidate_rankings:
            for rank in voter:
                if rank[CAND] in active_candidates:
                    first_choice_votes[rank[CAND]] += 1
                    break

        least_votes = min(first_choice_votes.values())
        candidates_to_eliminate = [candidate for candidate, votes in first_choice_votes.items() if votes == least_votes]
        
        if len(candidates_to_eliminate) > 1:
            last_choice_counts = {candidate: 0 for candidate in candidates_to_eliminate}
            for voter in candidate_rankings:
                for rank in reversed(voter):
                    if rank[CAND] in candidates_to_eliminate:
                        last_choice_counts[rank[CAND]] += 1
                        break
            most_last_votes = max(last_choice_counts.values())
            candidate_to_eliminate = [candidate for candidate, votes in last_choice_counts.items() if votes == most_last_votes][0]
        else:
            candidate_to_eliminate = candidates_to_eliminate[0]

        active_candidates.remove(candidate_to_eliminate)
        elimination_order.append(candidate_to_eliminate)

        for voter in candidate_rankings:
            voter[:] = [rank for rank in voter if rank[CAND] != candidate_to_eliminate]
    
    winner = active_candidates.pop()
    return winner, elimination_order, candidate_rankings

def create_voting(voters, candidates):
    numpy.random.seed(1052)
    candidateRanking = []
    for _ in range(voters):
        scores = numpy.random.normal(50, 20, candidates)
        scores = numpy.clip(scores, 0, 100)
        rankings = sorted(range(1, candidates + 1), key=lambda x: scores[x-1], reverse=True)
        voterRanking = [[rankings[i], scores[rankings[i]-1], i+1] for i in range(candidates)]
        candidateRanking.append(voterRanking)
    return candidateRanking

def calculate_social_welfare(candidate_rankings, winner):
    cardinal_utilities = []
    ordinal_utilities = []
    for voter in candidate_rankings:
        winner_score = next((rank[SCORE] for rank in voter if rank[CAND] == winner), 0)
        first_choice_score = voter[0][SCORE]
        cardinal_utility = abs(first_choice_score - winner_score)
        ordinal_utilities.append(abs(voter[0][PLACE] - next((rank[PLACE] for rank in voter if rank[CAND] == winner), 0)))
        cardinal_utilities.append(cardinal_utility)
    return sum(cardinal_utilities), sum(ordinal_utilities)


def print_connections(connections):
    print("CONNECTIONS")
    for row in connections:
        print(' '.join(str(val) for val in row))


def print_voter_preferences(candidate_rankings, message="Voter preferences:"):
    print(message)
    for i, voter in enumerate(candidate_rankings, start=1):
        print(f"Voter {i}: ", end="")
        for rank in voter:
            print(f"{rank[CAND]} (Score: {rank[SCORE]}, Rank: {rank[PLACE]}), ", end="")
        print()  

def simulate_strategic_voting(connections, candidate_rankings):
    voters = len(candidate_rankings)
    candidates = len(candidate_rankings[0])
    changes_made = True
    round = 1

    while changes_made:
        changes_made = False
        changes_count = 0

        popularity = {i+1: 0 for i in range(candidates)}
        for ranking in candidate_rankings:
            popularity[ranking[0][CAND]] += 1
            for i in range(voters):
                current_first_choice = candidate_rankings[i][0][CAND]
                connection_popularity = {candidate: 0 for candidate in range(1, candidates + 1)}
                for j in range(voters):
                    if connections[i][j] == 1:
                        first_choice_of_j = candidate_rankings[j][0][CAND]
                        connection_popularity[first_choice_of_j] += 1
                
                most_popular_among_connections = max(connection_popularity, key=connection_popularity.get)
                
                if most_popular_among_connections != current_first_choice:
                    candidate_rankings[i].sort(key=lambda rank: rank[CAND] == most_popular_among_connections, reverse=True)
                    changes_made = True
                    changes_count += 1
                    break
        if changes_count > 0:
            print(f"Round {round}: {changes_count} voters changed their minds.")
        else:
            print(f"Proceeding.")


    if round == 2:
        print("No voters changed their minds.")

def determine_plurality_winner(candidate_rankings):
    tally = {}
    for voter_rankings in candidate_rankings:
        first_choice = voter_rankings[0][CAND]
        if first_choice in tally:
            tally[first_choice] += 1
        else:
            tally[first_choice] = 1
    
    winner = max(tally, key=tally.get)
    return winner

def validate_rankings(candidate_rankings, voters, candidates):
    for voter_ranking in candidate_rankings:
        if len(voter_ranking) != candidates:
            return False
        ranked_candidates = [rank[CAND] for rank in voter_ranking]
        if len(set(ranked_candidates)) != candidates:
            return False
    return True

def calculate_social_welfare_based_on_initial(candidate_rankings, winner, initial_preferences):
    cardinal_utilities = []
    ordinal_utilities = []
    for idx, voter in enumerate(candidate_rankings):
        initial_first_choice = initial_preferences[idx]
        winner_score = next((rank[SCORE] for rank in voter if rank[CAND] == winner), None)
        initial_first_choice_score = next((rank[SCORE] for rank in voter if rank[CAND] == initial_first_choice), None)
        
        if winner_score is not None and initial_first_choice_score is not None:
            cardinal_utility = abs(initial_first_choice_score - winner_score)
            ordinal_difference = abs(voter[0][PLACE] - next((rank[PLACE] for rank in voter if rank[CAND] == initial_first_choice), 0))
            cardinal_utilities.append(cardinal_utility)
            ordinal_utilities.append(ordinal_difference)
    
    return sum(cardinal_utilities), sum(ordinal_utilities)


if __name__ == '__main__':
    voters = 15 
    candidates = 3
    candidate_rankings = create_voting(voters, candidates)

    if not validate_rankings(candidate_rankings, voters, candidates):
        print("Error: Invalid candidate rankings.")
    else:
        initial_preferences = [ranking[0][CAND] for ranking in candidate_rankings]
        connections = [[numpy.random.randint(0, 2) for _ in range(voters)] for _ in range(voters)]

        print_connections(connections)
        print_voter_preferences(candidate_rankings, "Voter preferences before strategic voting:")

        simulate_strategic_voting(connections, candidate_rankings)

        final_tally = {candidate: 0 for candidate in range(1, candidates + 1)}
        for ranking in candidate_rankings:
            final_tally[ranking[0][CAND]] += 1

        winner = max(final_tally, key=final_tally.get)


        print(f"Final vote tally: {final_tally}")
        print(f"Final Winner by Plurality: {winner}")

        cardinal_welfare, ordinal_welfare = calculate_social_welfare_based_on_initial(candidate_rankings, winner, initial_preferences)
        
        print(f"Cardinal Social Welfare: {cardinal_welfare}")
        print(f"Ordinal Social Welfare: {ordinal_welfare}")
