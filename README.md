# NicknameGenerator

This project was for my course on Advanced Natural Language Processing where I answered the research question: “Is there a preference for 
being addressed with certain type of nickname during an interaction with an agent?”

## Details

The interface for the agent was designed using HTML, CSS and Javascript using the Eel library for python. The program generates two kinds 
of nicknames: ones that rhyme with the user's name, and ones that are related to the interests of the user (personal nickname).

## Functionality

For the rhyming nickname the pronouncing library is used to find the pronunciation of the user's name, words in WordNet are found with 
similar pronunciation and the sentiment is found in SentiWordNet to make sure the word isn't insulting or negative. This method doesn't
always work well with names in languages that aren't English. The personal nickname is generated using ConceptNet, to find relevant terms 
sports that are entered; webscraping to find movie names related to the genre the user enters regarding preference for movies.

This program was written in a bit of a hurry so please excuse the organization of some of the functions, and the lack of classes.
