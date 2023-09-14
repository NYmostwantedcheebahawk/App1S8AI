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


condition1(Env) :- (findall(Red, (member(Red, Env), Red = red), Reds), count_items(Reds,N), N > 1),
member(silver, Env).
condition2(Env) :- \+ member(red,Env),(check_last_item(Env,yellow)).
condition3(Env) :- (findall(Blue, (member(Blue, Env), Blue = blue), Blues), count_items(Blues,N), N = 1).
condition4(Env) :- (findall(Yellow, (member(Yellow, Env), Yellow = yellow), Yellows), count_items(Yellows,N), N > 1).

obtainKey(Env,Res) :- (condition1(Env), find_all_indices(red, Env,Res)); (condition2(Env), 
Res = first); (condition3(Env), Res = first); (condition4(Env), Res = fourth); 
\+ (condition1(Env), condition2(Env), condition3(Env), condition4(Env)), Res = second.