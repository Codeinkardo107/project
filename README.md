Template for creating and submitting MAT496 capstone project.

# Overview of MAT496

In this course, we have primarily learned Langgraph. This is helpful tool to build apps which can process unstructured `text`, find information we are looking for, and present the format we choose. Some specific topics we have covered are:

- Prompting
- Structured Output 
- Semantic Search
- Retreaval Augmented Generation (RAG)
- Tool calling LLMs & MCP
- Langgraph: State, Nodes, Graph

We also learned that Langsmith is a nice tool for debugging Langgraph codes.

------

# Capstone Project objective

The first purpose of the capstone project is to give a chance to revise all the major above listed topics. The second purpose of the capstone is to show your creativity. Think about all the problems which you can not have solved earlier, but are not possible to solve with the concepts learned in this course. For example, We can use LLM to analyse all kinds of news: sports news, financial news, political news. Another example, we can use LLMs to build a legal assistant. Pretty much anything which requires lots of reading, can be outsourced to LLMs. Let your imagination run free.


-------------------------

# Project report Template

## Title: AI Fitness Goal Coach

## Overview

My project is a personalized training guidance system that helps users achieve specific fitness or calisthenics goals such as muscle-ups, handstands, planche progressions or general strength development. It also gives a link to follow tutorial for any exercise if you don't know how to perfomr it correctly(Form is a very important factor). It also provides a dailt nutrition plan including calories consumed, water content, protein content, carbs content, fats content. Unlike traditional workout plans that follow a fit approach, this system creates a customized, step-by-step progression plan based entirely on the user’s current fitness level, available equipment, time constraints, and desired goal.

After user gives their input they are given a preview of what a single day is like, then the user is asked if he needs to change the time or number of day. The system will modify future steps accordingly. Overall, this project focuses on simplicity, safety, and offering a smart and adaptable way to reach fitness goals without needing a coach, gym membership, or prior experience or needing to search the web and then calculate the schedule and nutritoin plan.

## Reason for picking up this project

I was interested in calesthenics, but was unable to do so because I wasn't able to get much information on my own, as well as reaching out to people didn't help much. So I thought of making a project on this. This project would help me in progress and in curernt health status.

## Video Summary Link: 

Make a short -  3-5 min video of yourself, put it on youtube/googledrive, and put its link in your README.md.

- you can use this free tool for recording https://screenrec.com/
- Video format should be like this:
- your face should be visible
- State the overall job of your agent: what inputs it takes, and what output it gives.
- Very quickly, explain how your agent acts on the input and spits out the output. 
- show an example run of the agent in the video


## Plan

I plan to execute these steps to complete my project.

- [DONE] Step 1: Project Setup - Defined file structure, environment variables, and dependencies.
- [DONE] Step 2: Core Logic Implementation - Created Pydantic models for structured user input and workout plans.
- [DONE] Step 3: RAG Pipeline - Implemented web search (Tavily), content scraping
- [DONE] Step 4: vector embedding (ChromaDB) for context-aware advice.
- [DONE] Step 5: Feasibility Check - Added logic to assess if the user's goal is realistic within the timeframe.
- [TODO] Step 6: Create Schedule -  Added logic to create a weekly schedule for given goal.
- [TODO] Step 7: Nutrition Integration - Implemented a parallel node to generate a nutrition plan alongside the workout schedule. Added logic for saving output to file.
- [TODO] Step 8: Feedback Loop - Added a "Human-in-the-loop" cycle to allow users to review and modify the plan before saving.
- [TODO] Step 9: Graph Construction - Built the LangGraph workflow with nodes for profiling, searching, and scheduling.
- [TODO] Step 10: Visualization & Output - Implemented graph visualization (with remote fallback) and Markdown file generation with resource links.
- [TODO] Step 11: Final Polish - Refined error handling and verified end-to-end functionality.

## Conclusion:

I had planned to achieve {this this}. I think I have/have-not achieved the conclusion satisfactorily. The reason for your satisfaction/unsatisfaction.

----------

# Added instructions:

- This is a `solo assignment`. Each of you will work alone. You are free to talk, discuss with chatgpt, but you are responsible for what you submit. Some students may be called for viva. You should be able to each and every line of work submitted by you.

- `commit` History maintenance.
  - Fork this repository and build on top of that.
  - For every step in your plan, there has to be a commit.
  - Change [TODO] to [DONE] in the plan, before you commit after that step. 
  - The commit history should show decent amount of work spread into minimum two dates. 
  - **All the commits done in one day will be rejected**. Even if you are capable of doing the whole thing in one day, refine it in two days.  
 
 - Deadline: Dec 2nd, Tuesday 11:59 pm


# Grading: total 25 marks

- Coverage of most of topics in this class: 20
- Creativity: 5
  