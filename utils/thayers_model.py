def thayers_mood_model(valence, energy):
    """
    Implements Thayer's two-dimensional mood model
    Returns mood quadrant based on valence and energy
    """
    if valence > 0.5 and energy > 0.5:
        return "Happy/Excited"
    elif valence > 0.5 and energy <= 0.5:
        return "Content/Calm"
    elif valence <= 0.5 and energy > 0.5:
        return "Anxious/Tense"
    else:
        return "Sad/Depressed"


def cultural_adjusted_thayers(valence, energy, cultural_factor=1.0, artist_origin=None):
    origin_factors = {
        #afrobeat - high energy
        'Nigeria': 1.8,  
        #more subdued energy
        'Japan': 0.9,     
        #high energy
        'Brazil': 1.6,    
        #default
        None: 1.0         
    }
    
    factor = cultural_factor if cultural_factor else origin_factors.get(artist_origin, 1.0)
    adjusted_energy = min(1.0, energy * factor)  # Cap at 1.0
    
    return {
        'quadrant': thayers_mood_model(valence, adjusted_energy),
        'adjusted_energy': adjusted_energy,
        'original_energy': energy
    }



# # Add mood intensity scoring and better cultural adjustments
# def mood_intensity(valence, energy):
#     """Calculate a 0-100 mood intensity score"""
#     return min(100, int((valence * 0.6 + energy * 0.4) * 100))

# def cultural_adjusted_thayers(valence, energy, cultural_factor=1.0, artist_origin=None):
#     """
#     Enhanced with:
#     - Origin-specific defaults
#     - Energy capping
#     - Detailed return object
#     """
#     origin_factors = {
#         'Nigeria': 1.3,  # Afrobeat
#         'Japan': 0.9,     # More subdued
#         'Brazil': 1.2,    # High-energy
#         None: 1.0
#     }
    
#     factor = cultural_factor if cultural_factor else origin_factors.get(artist_origin, 1.0)
#     adjusted_energy = min(1.0, energy * factor)
    
#     return {
#         'quadrant': thayers_mood_model(valence, adjusted_energy),
#         'adjusted_energy': adjusted_energy,
#         'original_energy': energy,
#         'intensity': mood_intensity(valence, adjusted_energy)
#     }