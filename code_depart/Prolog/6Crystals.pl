% Define the helper predicates
not_member(_, []).
not_member(X, [H|T]) :- X \= H, not_member(X, T).

count_items([], 0).
count_items([_|T], N) :- count_items(T, N1), N is N1 + 1.

% Define condition1/1 and condition3/1 based on your provided conditions
condition1(Env) :- not_member(yellow, Env), member(bronze, Env).
condition2(Env) :- (findall(Yellow, (member(Yellow, Env), Yellow = yellow), Yellows), count_items(Yellows, N), N = 1), (findall(White, (member(White, Env), White = white), Whites), count_items(Whites, N), N > 1).
condition3(Env) :- findall(Red, (member(Red, Env), Red = red), Reds), count_items(Reds, N), N = 0.

% Define obtainKey/2 using the conditions
obtainKey(Env, Res) :-
    (condition1(Env), Res = third) ;  % If condition1 is true, set Res to third
    (condition2(Env), Res = fourth) ;  % If condition1 is true, set Res to third
    (condition3(Env), Res = sixth) ;  % If condition3 is true, set Res to sixth
    \+ (condition1(Env); condition2(Env) ; condition3(Env)), Res = fourth.


