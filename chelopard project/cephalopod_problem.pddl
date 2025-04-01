(define (problem cephalopod-instance)
  (:domain chephalopod_domain)
  (:objects
    cella-0-0 - cella
    cella-0-1 - cella
    cella-0-2 - cella
    cella-0-3 - cella
    cella-0-4 - cella
    cella-1-0 - cella
    cella-1-1 - cella
    cella-1-2 - cella
    cella-1-3 - cella
    cella-1-4 - cella
    cella-2-0 - cella
    cella-2-1 - cella
    cella-2-2 - cella
    cella-2-3 - cella
    cella-2-4 - cella
    cella-3-0 - cella
    cella-3-1 - cella
    cella-3-2 - cella
    cella-3-3 - cella
    cella-3-4 - cella
    cella-4-0 - cella
    cella-4-1 - cella
    cella-4-2 - cella
    cella-4-3 - cella
    cella-4-4 - cella
    umano - giocatore
    avversario AI - giocatore
    dado-2-2 - dado
    dado-3-2 - dado
    dado-2-3 - dado
    dado-3-1 - dado
    dado-2-1 - dado
    dado-0-4 - dado
    valore-1 - valore
    valore-2 - valore
    valore-3 - valore
    valore-4 - valore
    valore-5 - valore
    valore-6 - valore
  )
  (:init
    (occupata cella-2-2)
    (dado_appartiene_a dado-2-2 umano)
    (valore_dado dado-2-2 valore-1)
    (occupata cella-3-2)
    (dado_appartiene_a dado-3-2 umano)
    (valore_dado dado-3-2 valore-3)
    (occupata cella-2-3)
    (dado_appartiene_a dado-2-3 umano)
    (valore_dado dado-2-3 valore-5)
    (occupata cella-3-1)
    (dado_appartiene_a dado-3-1 avversario AI)
    (valore_dado dado-3-1 valore-1)
    (occupata cella-2-1)
    (dado_appartiene_a dado-2-1 avversario AI)
    (valore_dado dado-2-1 valore-2)
    (occupata cella-0-4)
    (dado_appartiene_a dado-0-4 avversario AI)
    (valore_dado dado-0-4 valore-1)
    (turno umano)
  )
  (:goal (exists (?c - cella) (occupata ?c)))
)
