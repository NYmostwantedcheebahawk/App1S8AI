count_items([], 0).
count_items([_|T], N) :- count_items(T, N1), N is N1 + 1.

check_last_item([ColorMatch], ColorMatch).

check_last_item([_|T], ColorMatch) :-
    check_last_item(T, ColorMatch).

check_last_item(_, _) :- false.


condition1(Env) :- check_last_item(Env,black), member(gold, Env).
condition2(Env) :- (findall(Red, (member(Red, Env), Red = red), Reds), count_items(Reds,N), N = 1), 
(findall(Yellow, (member(Yellow, Env), Yellow = yellow), Yellows), count_items(Yellows,N2), N2 > 1).
condition3(Env) :- \+ member(black,Env).

obtainKey(Env,Res) :- condition1(Env), Res = fourth; condition2(Env), Res = first; 
condition3(Env), Res = second; \+ (condition1(Env), condition2(Env), condition3(Env)), Res = first.