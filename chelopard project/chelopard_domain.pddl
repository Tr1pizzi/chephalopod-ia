;file di dominio chephalopod
;Header and description

(define (domain chephalopod_domain)

;remove requirements that are not needed(TEOria estensione pddl :nel momento incui scrivi la parola chiave define domain ti appaiono tutti i campi che sono definibili)
(:requirements :strips :typing :negative-preconditions)
(:types cella dado giocatore valore)

(:predicates 
(occupata ?c - cella)
(dado_appartiene_a ?d - dado ?p - giocatore)
(valore_dado ?d - dado ?v -valore)
(adiacenti ?c1 - cella ?c2 - cella)
(turno ?p - giocatore)
)  

;define actions here
(:action piazzo_dado
    :parameters (?p - giocatore ?d - dado ?c - cella ?v -valore)
    :precondition (and (not (occupata ?c)) (turno ?p))
    :effect (and (occupata ?c) (dado_appartiene_a ?d ?p) (valore_dado ?d ?v) (not (turno ?p))))


(:action cattura_dado
    :parameters (?p - giocatore ?c - cella)
    :precondition (and (occupata ?c) (exists (?c1 - cella) (and (adiacenti ?c ?c1) (occupata ?c1))))
    :effect (and )
)
  (:action cambio_turno
    :parameters (?p1 - giocatore ?p2 - giocatore)
    :precondition (turno ?p1)
    :effect (and (not (turno ?p1)) (turno ?p2)))
)

