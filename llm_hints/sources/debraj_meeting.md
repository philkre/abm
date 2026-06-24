## **Research questions/notes**

- Look for parameter regime where survival is possible (if it exists)
    - Analytically no, stable fixed point is depleted.
    - Oscillation maybe
- Sensitivity parameters
    - Beta (fermi temp)
    - Delta/gamma (recovery / depletion rates of env)
    - Lambda (loss aversion)
    - E0, flood probability center
    - K, steepness of prob
    - 
- still interesting to have a wealth gradient (spatial heterogeneity in environment/etc)
- remove sigmoid / less parameters
- “wealth” → it is not real wealth but rather the amount of money the community has to spend on defences against floods specifically. Currently we model this as a portfolio that grows with an interest rate which might not be the most realistic scenario: individuals in the community would have to put their money into some kind of portfolio to earn an interest which seems unrealistic. Should we scrap the concept for a flat savings account without interest?
    - scalefree distribution for wealth?

## Debraj questions

- Verify whether our mechanics make sense at all
    - explain current situation and motivation
    - thinking about removing g / income mechanics
- Struggle to find interesting narative
    - a research question for which there is an interesting hypothesis (which is not a trivial fixed point)
        
        “Look for parameter regime where survival is possible (if it exists)” 
        
- Discuss sensitivity analysis parameter candidates
    
    

## Debraj responses

- Interesting to look at the oscillating tragedy of commons
    - i.e. “can we reproduce the weitz result in our model”
- throw out initialization params (keep fixed)
- obvious choice for sensitivity candidates is the ones that help identify hypothesis
    - what parameters is our research question about, this should guide the sensitivity analysis
- look for parameters that are relative to each other / related (condense them)
- unless the fixed parameters can be calibrated, an educated guess is needed
    - e.g. look for geography, otherwise it’s just a guess
- strength of the environmental feedback is always interesting
    - env / disaster response
    - disaster prob
    - if they are relative, keep one fixed and scale the other
- loss aversion and wealth distribution are related to each other also
    - initial loss aversion is important, but wealth distribution not so much
    - log normal distribution for wealth suggested
- keep heterogeneous outside of sensitivity, do scatter plot for heterogenous input vs output
    - don’t put parameters that heterogeneously distributed in sens anal, but do sweep
- migration?
    - interesting ofc, but no
- spatial distribution (gradient)
    - too complicated to conclude relationship/causality
- best to anchor everything to a research question,
    - oscillating tragedy of commons is interesting
    - isolating influence of floods
    - punctuated equilbrium
        - if it moves between states
    - the trivial fixed points may be a scaling problem
        - try to categorize them,
        - radar plot
        - **finding phases**
- Income could be a wiener process, too
    - or work in bounded 0-1 scale!
- keep the scale in check
    - otherwise mundane dynamics

## Conclusions

- Sensitivity params
    - fermi selection strength \beta
    - flood severity (\ell, \eta)