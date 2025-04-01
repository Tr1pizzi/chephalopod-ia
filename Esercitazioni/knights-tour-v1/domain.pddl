(define (domain knights-tour)
    (:requirements :negative-preconditions)

    (:predicates
        (at ?square)
        (visited ?square)
        (valid_move ?square_from ?square_to)
    )

    (:action move
        :parameters (?from ?to)
        :precondition (and (at ?from)
            (valid_move ?from ?to)
            (not (visited ?to)))
        :effect (and 
            (not (at ?from))
            (at ?to)
            (visited ?to))
    )
)