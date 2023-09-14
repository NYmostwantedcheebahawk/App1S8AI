count_items([], 0).
count_items([_|T], N) :- count_items(T, N1), N is N1 + 1.

check_last_item([ColorMatch], ColorMatch).

check_last_item([_|T], ColorMatch) :-
    check_last_item(T, ColorMatch).

check_last_item(_, _) :- false.
	
	
find_indices(Element, [Element|Rest], [Index|Indices], CurrentIndex) :-
    NewCurrentIndex is CurrentIndex + 1,
    find_indices(Element, Rest, Indices, NewCurrentIndex),
    Index is CurrentIndex.

find_indices(Element, [_|Rest], Indices, CurrentIndex) :-
    NewCurrentIndex is CurrentIndex + 1,
    find_indices(Element, Rest, Indices, NewCurrentIndex).

find_indices(_, [], [], _).

find_all_indices(Element, List, Indices) :-
    find_indices(Element, List, Indices, 0).
	


condition1(Env) :- \+ member(red,Env).
condition2(Env) :- check_last_item(Env,white).
condition3(Env) :- (findall(Blue, (member(Blue, Env), Blue = blue), Blues), count_items(Blues,N), N  > 1).

obtainKey(Env,Res) :- (condition1(Env), Res = second); (condition2(Env), Res = three); (condition3(Env), find_all_indices(blue,Env,Res));
\+ (condition1(Env), condition2(Env), condition3(Env)), Res = first.