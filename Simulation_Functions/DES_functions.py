import math
import random
######################################################## Setting Parameters #################################################################
#Note: Triangular funciton is (low, high, mode)
def arrival_time(arrival_gen, lam_user_arrival):
    time = arrival_gen.expovariate(lam_user_arrival)
    return time 

def OR_death_time(now,params, death_gen):
    days_per_year = params["days_per_year"]
    start_year = params["start_year"]
    LNmean_deathdays = params["LNmean_deathdays"]
    LNsigma_deathdays = params["LNsigma_deathdays"]

    # time = max_deathdays*death_gen.betavariate(BetaA1_deathdays,BetaA2_deathdays)
    year_shift = 2019
    if now <= days_per_year*(year_shift - start_year):
        time = death_gen.lognormvariate(LNmean_deathdays[0],LNsigma_deathdays[0])
    else:
        time = death_gen.lognormvariate(LNmean_deathdays[1],LNsigma_deathdays[1])
    return time

def Ocrime_time(crime_gen, params):
    LNmean_Oarrestdays = params["LNmean_Oarrestdays"]
    LNsigma_Oarrestdays = params["LNsigma_Oarrestdays"]
    time = crime_gen.lognormvariate(LNmean_Oarrestdays,LNsigma_Oarrestdays)
    # time = max_arrestdays*crime_gen.betavariate(BetaA1_arrestdays,BetaA2_arrestdays)
    return time

def nonOcrime_time(crime_gen, params):
    LNmean_nonOarrestdays = params["LNmean_nonOarrestdays"]
    LNsigma_nonOarrestdays = params["LNsigma_nonOarrestdays"]
    time = crime_gen.lognormvariate(LNmean_nonOarrestdays,LNsigma_nonOarrestdays)
    # time = max_arrestdays*crime_gen.betavariate(BetaA1_arrestdays,BetaA2_arrestdays)
    return time

def treat_time(treat_gen, params):
    LNmean_treatdays = params["LNmean_treatdays"]
    LNsigma_treatdays = params["LNsigma_treatdays"]
    time = treat_gen.lognormvariate(LNmean_treatdays,LNsigma_treatdays)
    # time = max_treatdays*treat_gen.betavariate(BetaA1_treatdays,BetaA2_treatdays)
    return time

def hosp_time(hosp_gen, params):
    LNmean_hospdays = params["LNmean_hospdays"]
    LNsigma_hospdays = params["LNsigma_hospdays"]
    time = hosp_gen.lognormvariate(LNmean_hospdays,LNsigma_hospdays)
    # time = max_hospdays*hosp_gen.betavariate(BetaA1_hospdays,BetaA2_hospdays)
    return time
def alldeath_time(loopdone, alldeath_gen, params):
    dup_prev_age_mean = params["dup_prev_age_mean"]
    dup_prev_age_sig = params["dup_prev_age_sig"]
    dup_init_age_mean = params["dup_init_age_mean"]
    dup_init_age_sig = params["dup_init_age_sig"]
    #Based on Lewer 2020 age histogram ofdrug using cohort in australia
    if loopdone == False: #prevalence age distribtuion
        age = 12+ alldeath_gen.lognormvariate(dup_prev_age_mean,dup_prev_age_sig)
    else: #initiation age distribtuion
        age = 12 + alldeath_gen.lognormvariate(dup_init_age_mean, dup_init_age_sig)
    if age >101:
        age = 100
    index_age = math.floor((age/5)-2)
    deathAge_ranges = [x for x in range(math.floor(age/5)*5,101,5)]
    #based on adjusted death rates for non-drug abuse 1999-2001
    num_surviving = [99098,99000,98677,98245,97830,97330,96620,95556,93956,91626,88047,82727,75263,64974,51153,34705,18602,6921,1489]
    num_die= [98, 323, 432, 414,500,710,1065,1600,2330,3579,5320,7464,10289,13821,16449,16103,11681,5432,1489]
    LIFE_exp_probs = []
    for x in range(index_age, len(num_surviving)):
        LIFE_exp_probs.append(num_die[x]/num_surviving[index_age])
    rand_deathAgegroup = alldeath_gen.choices(deathAge_ranges, weights=LIFE_exp_probs, k=1)
    rand_deathAgegroup= float(rand_deathAgegroup[0])
    if age > rand_deathAgegroup:
        time = alldeath_gen.uniform(age*365.25,(rand_deathAgegroup+5)*365.25) - age*365.25
    else:
        time = alldeath_gen.uniform(rand_deathAgegroup*365.25,(rand_deathAgegroup+5)*365.25) - age*365.25
    return time, age


def inactive_time(inactive_gen, params): 
    LNmean_iadays = params["LNmean_iadays"]
    LNsig_iadays = params["LNsig_iadays"]
    time = inactive_gen.lognormvariate(LNmean_iadays,LNsig_iadays)
    return time
def service_time(Itype, service_gen, params):
    LNmean_crimeservice = params["LNmean_crimeservice"]
    LNsig_crimeservice = params["LNsig_crimeservice"]
    LNmean_treatservice = params["LNmean_treatservice"]
    LNsig_treatservice = params["LNsig_treatservice"]
    LNmean_hospservice = params["LNmean_hospservice"]
    LNsig_hospservice = params["LNsig_hospservice"]
    if Itype == 'crime':
        time = service_gen.lognormvariate(LNmean_crimeservice,LNsig_crimeservice) 
    elif Itype == 'treatment':    
        time = service_gen.lognormvariate(LNmean_treatservice,LNsig_treatservice) 
    elif Itype == 'hosp':
        time = service_gen.lognormvariate(LNmean_hospservice,LNsig_hospservice) 
    elif Itype == 'inactive': #no service time for individuals not actively using only set a relapse time (aka time in inactive state)
        time = 0
    return time

def relapse_time(Itype, ArrivalTime, CurrentTime, gen_dict, params): #estimate of time until next use
    relapse_gen = gen_dict["relapse_gen"]
    start_gen = gen_dict["start_gen"]
    starting_probs = params["starting_probs"]
    LNmean_crimerel = params["LNmean_crimerel"]
    LNsig_crimerel = params["LNsig_crimerel"]
    LNmean_treatrel = params["LNmean_treatrel"]
    LNsig_treatrel = params["LNsig_treatrel"]
    LNmean_hosprel = params["LNmean_hosprel"]
    LNsig_hosprel = params["LNsig_hosprel"]
    LNmean_iarel = params["LNmean_iarel"]
    LNsig_iarel = params["LNsig_iarel"]
    LNmean_crimerel = params["LNmean_crimerel"]
    LNsig_crimerel = params["LNsig_crimerel"]
    LNmean_treatrel = params["LNmean_treatrel"]
    LNsig_treatrel = params["LNsig_treatrel"]
    LNmean_hosprel = params["LNmean_hosprel"]
    LNsig_hosprel = params["LNsig_hosprel"]
    LNmean_iarel = params["LNmean_iarel"]
    LNsig_iarel = params["LNsig_iarel"]
    if ArrivalTime == 0 and CurrentTime == 0:
        if  Itype == 'inactive': #split up starting inactive distribtuions
            # breakpoint()
            RN = start_gen.random()
            if RN <    (starting_probs[1] / starting_probs[4]): #arrest
                Itype = "crime"
            elif RN <    ((starting_probs[1] / starting_probs[4]) + (starting_probs[2]/ starting_probs[4])): #hospital
                Itype = "hosp"
            elif RN <    ((starting_probs[1] / starting_probs[4]) + (starting_probs[2]/ starting_probs[4])+(starting_probs[3]/ starting_probs[4])): #treatment
                Itype = "treatment"
        if Itype == 'crime': 
            time = relapse_gen.lognormvariate(LNmean_crimerel,LNsig_crimerel) 
        elif Itype == 'treatment':
            time = relapse_gen.lognormvariate(LNmean_treatrel,LNsig_treatrel) 
            # alternative option to break up - percent of people that complete treatment:
            # if they complete treatment
            # if they don't complete treatment    
        elif Itype == 'hosp':
            time = relapse_gen.lognormvariate(LNmean_hosprel,LNsig_hosprel) 
        else:
            time = relapse_gen.lognormvariate(LNmean_iarel,LNsig_iarel) 
    else:
        if Itype == 'crime': 
            time = relapse_gen.lognormvariate(LNmean_crimerel,LNsig_crimerel) 
        elif Itype == 'treatment':
            time = relapse_gen.lognormvariate(LNmean_treatrel,LNsig_treatrel)   
        elif Itype == 'hosp':
            time = relapse_gen.lognormvariate(LNmean_hosprel,LNsig_hosprel)
        elif  Itype == 'inactive': 
            time = relapse_gen.lognormvariate(LNmean_iarel,LNsig_iarel)
    return time

def setDead(self):
        time = min(self.timeofNonOpioidDeath,self.timeofFatalOD)
        time = max(time,0)
        yield self.env.timeout(time)
    
def getUserType(self):
    if self.user_type == 'nru':
        return 'non-relapsed user'
    elif self.user_type == 'rnu':
        return 'recovering non-user'
    elif self.user_type == 'ru':
        return 'relapsed user'
    else:
        return 'deceased'
    

