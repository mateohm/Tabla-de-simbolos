# Tabla de simbolos

## Introducción

El presente trabajo desarrolla los componentes fundamentales del proceso de compilación para un subconjunto de lenguajes de programación, específicamente tomando como base una gramática inspirada en C. El objetivo principal es construir una gramática formal, definir su ETDS (Estructura de Datos para el Árbol Sintáctico) junto con su respectiva tabla de símbolos, y finalmente implementar un generador de código intermedio en tres direcciones (TAC) a partir del AST.

Este proceso representa las etapas esenciales de un compilador: desde la especificación formal del lenguaje, pasando por la representación interna del programa, hasta la generación de un código intermedio que sirve como puente entre el análisis semántico y la optimización o generación de código final. El proyecto está organizado para ser claro, modular, extensible y totalmente funcional para propósitos académicos.


## Desarrollo

1. Definición de la Gramática

Se diseñó una gramática libre de contexto en notación BNF para un subconjunto de C, permitiendo estructuras como:

- Declaraciones de variables

- Declaración de funciones

- Bloques {}

- Estructuras condicionales (if / else)

- Bucles (while)

- Retornos

- Expresiones aritméticas y lógicas

- Llamadas a funciones

La gramática se guardó en un archivo .txt, con el fin de documentar y permitir su uso en herramientas de análisis sintáctico.


2. ETDS (Estructura de Datos del AST)

A partir de la gramática, se definieron las clases que representan los nodos del Árbol Sintáctico Abstracto (AST).
La ETDS permite modelar cada componente del lenguaje mediante:

- Nodos de declaración (VarDecl, FuncDecl)

- Nodos de control (IfStmt, WhileStmt)

- Nodos de expresiones (BinaryOp, UnaryOp, Assignment)

- Nodos de valores (Identifier, IntLiteral)

- Bloques y sentencias

El AST es la representación estructural más importante dentro del compilador, pues permite recorrer el programa sin depender directamente del código fuente.


3. Implementación de la Tabla de Símbolos
   
La tabla de símbolos se implementó como una pila de ámbitos (scopes), permitiendo manejar variables globales, locales, parámetros y funciones.
Cada símbolo almacena información relevante como:

- Nombre

- Tipo

- Clase (variable, parámetro o función)

- Nivel de anidamiento

- Lista de parámetros (si es función)

Esta estructura es esencial para el análisis semántico, detección de errores y para guiar la generación de código intermedio.

4. Generador de Código en Tres Direcciones (TAC)

Se implementó un módulo en Python que recorre el AST y genera instrucciones TAC, un formato intermedio simple y ampliamente utilizado en compiladores.
Las instrucciones generadas incluyen:

- Operaciones aritméticas y lógicas

- Asignaciones

- Saltos condicionales

- Manejo de etiquetas

- Llamadas a funciones

- Retornos

Cada expresión produce un temporal (t1, t2, …), y cada estructura de control genera etiquetas (L1, L2, …).
El resultado es un conjunto de instrucciones legibles y útiles para optimizaciones futuras o traducción a código máquina.
