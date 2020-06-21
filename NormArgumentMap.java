package namargumentationsystem;

import java.io.*;
import java.util.*;
import ww.*;

/**
 * This class implements the norm argument map, orginizes the arguments and
 * computes the overall support for the norm
 * 
 * @author Marc
 */
public class NormArgumentMap {

	/**
	 * The norm debated
	 */
	private Norm norm;
	/**
	 * The arguments in favor of the norm
	 */
	private ArgumentSet positiveArgs;
	/**
	 * The arguments against the norm
	 */
	private ArgumentSet negativeArgs;
	/**
	 * The opinion spectrum of the norm argument map
	 */
	private Spectrum spec;
	/**
	 * The alpha to compute the alpha-relevant arguments
	 */
	private double alpha;

	private double originalNormSupport;

	private double originalArgsNum;

	private String implementationInfo;

	/**
	 * Creates a new norm argument map
	 * 
	 * @param n    the norm argument map's norm
	 * @param spec the norm argument map's spectrum
	 */
	public NormArgumentMap(Norm n, Spectrum spec) {
		this(n, DEFAULT.alpha(), spec, DEFAULT.importanceFunction(spec));
	}

	/**
	 * Creates a new norm argument map
	 * 
	 * @param n    the norm argument map's norm
	 * @param spec the norm argument map's spectrum
	 * @param i    the norm argument map's importance function
	 */
	public NormArgumentMap(Norm n, Spectrum spec, ImportanceFunction i) {
		this(n, DEFAULT.alpha(), spec, i);
	}

	/**
	 * Creates a new norm argument map
	 * 
	 * @param n     the norm argument map's norm
	 * @param alpha the norm argument map's alpha
	 * @param spec  the norm argument map's spectrum
	 */
	public NormArgumentMap(Norm n, double alpha, Spectrum spec) {
		this(n, alpha, spec, DEFAULT.importanceFunction(spec));
	}

	/**
	 * Creates a new norm argument map
	 * 
	 * @param n     the norm argument map's norm
	 * @param alpha the norm argument map's alpha
	 * @param spec  the norm argument map's spectrum
	 * @param i     the norm argument map's importance function
	 */
	public NormArgumentMap(Norm n, double alpha, Spectrum spec, ImportanceFunction i) {
		this.norm = n;
		this.spec = spec;
		this.alpha = alpha;
		this.negativeArgs = new ArgumentSet(spec, i);
		this.positiveArgs = new ArgumentSet(spec, i);
	}

	/**
	 * Adds an argument to one of the two argument sets
	 * 
	 * @param a        the argument to add
	 * @param positive the set to add it to (true for positive arguments, false for
	 *                 negative arguments)
	 */
	public void addArgument(Argument a, Boolean positive) {
		if (a.in(this.spec)) {
			if (positive) {
				this.positiveArgs.addArgument(a);
			} else {
				this.negativeArgs.addArgument(a);
			}
		}
	}

	/**
	 * Creates and adds a new argument to one of the two argument sets
	 * 
	 * @param a        the string to create the argument to add
	 * @param positive the set to add it to (true for positive arguments, false for
	 *                 negative arguments)
	 */
	public void addArgument(String a, Boolean positive) {
		Argument arg = new Argument(a, this.spec, this.getImportanceFunction());
		if (positive) {
			this.positiveArgs.addArgument(arg);
		} else {
			this.negativeArgs.addArgument(arg);
		}
	}

	/**
	 * Computes the number of (all/alpha-relevant) argument's opinions in the norm
	 * argument map
	 * 
	 * @param relevant If true returns the number of all the alpha-relevant
	 *                 argument's opinions, otherwise the number of opinions of all
	 *                 the arguments
	 * @return double the number of (all/alpha-relevant) argument's opinions
	 */
	public double numberOpinions(Boolean relevant) {
		double result;
		if (relevant) {
			result = this.negativeArgs.numberRelevantOpinions(this.minimumOpinions())
					+ this.positiveArgs.numberRelevantOpinions(this.minimumOpinions());
		} else {
			result = this.negativeArgs.numberOpinions() + this.positiveArgs.numberOpinions();
		}
		return result;
	}

	/**
	 * Computes the minimum number of opinions that an argument has to have to be
	 * considered alpha-relevant
	 * 
	 * @param alpha the alpha to be considered alpha-relevant
	 * @return double the minimum number of opinions that an argument has to have to
	 *         be considered alpha-relevant
	 */
	public double minimumOpinions(double alpha) {
		double maximum = Double.NEGATIVE_INFINITY;
		List<Argument> a = this.negativeArgs.getArguments();
		for (int i = 0; i < a.size(); i++) {
			if (a.get(i).numberOpinions() > maximum) {
				maximum = a.get(i).numberOpinions();
			}
		}
		a = this.positiveArgs.getArguments();
		for (int i = 0; i < a.size(); i++) {
			if (a.get(i).numberOpinions() > maximum) {
				maximum = a.get(i).numberOpinions();
			}
		}
		return maximum * alpha;
	}

	/**
	 * Computes the minimum number of opinions that an argument has to have to be
	 * considered alpha-relevant taking the norm argument map's alpha
	 * 
	 * @return double the minimum number of opinions that an argument has to have to
	 *         be considered alpha-relevant
	 */
	public double minimumOpinions() {
		return this.minimumOpinions(this.alpha);
	}

	/**
	 * Computes the overall norm support
	 * 
	 * @param alpha the alpha to compute the alpha-relevant arguments
	 * @return double the support for the norm
	 */
	public double support(double alpha) {
		Vector<Double> wmweights = new Vector<Double>(2);
		Vector<Double> owaweights = new Vector<Double>(2);
		Vector<Double> data = new Vector<Double>(2);
		double result = Double.NaN;
		double minimum = this.minimumOpinions(alpha);
		data.addElement(this.positiveArgs.support(minimum));
		data.addElement(this.spec.symmetric(this.negativeArgs.support(minimum)));
		if (!data.get(0).isNaN()) {
			wmweights.addElement(this.positiveArgs.weight(minimum));
			owaweights.addElement(this.getImportanceFunction().compute(data.get(0)));
		} else {
			wmweights.addElement(0.);
			owaweights.addElement(0.);
		}
		if (!data.get(1).isNaN()) {
			wmweights.addElement(this.negativeArgs.weight(minimum));
			owaweights.addElement(this.getImportanceFunction().compute(data.get(1)));
		} else {
			wmweights.addElement(0.);
			owaweights.addElement(0.);
		}
		double total1 = owaweights.get(0) + owaweights.get(1);
		double total2 = wmweights.get(0) + wmweights.get(1);
		if (total1 != 0) {
			owaweights.set(0, owaweights.get(0) / total1);
			owaweights.set(1, owaweights.get(1) / total1);
		}
		if (total2 != 0) {
			wmweights.set(0, wmweights.get(0) / total2);
			wmweights.set(1, wmweights.get(1) / total2);
		}
		if (!data.get(0).isNaN()) {
			if (!data.get(1).isNaN()) {
				try {
					result = wwv2.wowa(owaweights, wmweights, data);
				} catch (Exception e) {
					System.err.println("Unable to compute WOWA for the norm support");
				}
			} else {
				result = data.get(0);
			}
		} else if (!data.get(1).isNaN()) {
			result = data.get(1);
		}
		return result;
	}

	/**
	 * Computes the overall support for the norm using the norm argument map's alpha
	 * to compute the alpha-relevant arguments
	 * 
	 * @return double the support for the norm
	 */
	public double support() {
		return this.support(this.alpha);
	}

	/**
	 * Prints the status of all the norm argument map, that is the status of each
	 * argument set (including the status of each argument in the set) and the
	 * support for the norm
	 * 
	 * @param out The PrintStream in which the information is printed
	 */
	public void printStatus(PrintStream out) {
		Double possupport = this.positiveArgs.support(this.minimumOpinions());
		Double negsupport = this.negativeArgs.support(this.minimumOpinions());
		Double normsupport = this.support();
		out.println("Norm:" + this.norm.getStatement());
		out.println("Spectrum:" + this.spec);
		out.println("Alpha: " + this.alpha);
		out.println(
				"\n   Results   \n-------------\n\nArguments in favor (argument, support, opinions recieved, alpha-relevance):");
		this.positiveArgs.printStatus(out, this.minimumOpinions());
		out.print("\nOverall support for the alpha-relevant arguments in favor: ");
		if (possupport.isNaN()) {
			out.println("Not defined");
		} else {
			out.format("%.4f\n", possupport);
		}
		out.println("\nArguments against (argument, support, opinions recieved, alpha-relevance):");
		this.negativeArgs.printStatus(out, this.minimumOpinions());
		out.print("\nOverall support for the alpha-relevant arguments against: ");
		if (negsupport.isNaN()) {
			out.println("Not defined");
		} else {
			out.format("%.4f\n", negsupport);
		}
		out.print("\nOverall support for the norm: ");
		if (normsupport.isNaN()) {
			out.println("Not defined");
		} else {
			out.format("%.4f\n", normsupport);
			this.originalNormSupport = normsupport;
		}

		this.originalArgsNum = this.positiveArgs.getArguments().size() + this.negativeArgs.getArguments().size();

		System.out.println("\n\n\n\n");
		HashMap currArgMap;

		Double mostImportantArgValue = -99.;
		HashMap mostImportantArg = new HashMap<>();

		for (int i = 0; i < this.positiveArgs.argumentData.size(); i++) {
			currArgMap = this.positiveArgs.argumentData.get(i);
			if ((boolean) currArgMap.get("is_relevant")) {
				printArgMap(currArgMap);
				if ((Double) currArgMap.get("weight") * (Double) currArgMap.get("support") > mostImportantArgValue) {
					mostImportantArgValue = (Double) currArgMap.get("weight") * (Double) currArgMap.get("support");
					mostImportantArg = currArgMap;
				}
			}
		}

		Double mostImportantArgValueNeg = -99.;
		HashMap mostImportantArgNeg = new HashMap<>();

		for (int i = 0; i < this.negativeArgs.argumentData.size(); i++) {
			currArgMap = this.negativeArgs.argumentData.get(i);
			if ((boolean) currArgMap.get("is_relevant")) {
				printArgMap(currArgMap);
				if ((Double) currArgMap.get("weight") * (Double) currArgMap.get("support") > mostImportantArgValueNeg) {
					mostImportantArgValueNeg = (Double) currArgMap.get("weight") * (Double) currArgMap.get("support");
					mostImportantArgNeg = currArgMap;
				}
			}
		}

		if (mostImportantArgValue != -99.) {
			System.out.println("\n\n\n\n");
			System.out.println("The most important + argument is: " + mostImportantArg.get("argument"));
			System.out.println("\tsupport = " + mostImportantArg.get("support"));
			System.out.println("\t# opinions = " + mostImportantArg.get("num_opinions"));
			System.out.println("\tImportance value = "
					+ (Double) mostImportantArg.get("weight") * (Double) mostImportantArg.get("support"));
			System.out.println("\n\n\n\n");
		}
		if (mostImportantArgValueNeg != -99.) {
			System.out.println("The most important - argument is: " + mostImportantArgNeg.get("argument"));
			System.out.println("\tsupport = " + mostImportantArgNeg.get("support"));
			System.out.println("\t# opinions = " + mostImportantArgNeg.get("num_opinions"));
			System.out.println("\tImportance value = "
					+ (Double) mostImportantArgNeg.get("weight") * (Double) mostImportantArgNeg.get("support"));
			System.out.println("\n\n\n\n");
		}

		out.print("\nOverall support for the norm: ");
		if (normsupport.isNaN()) {
			out.println("Not defined");
		} else {
			out.format("%.4f\n", normsupport);
		}

		
		//tfg(out, this.positiveArgs, mostImportantArg, this.negativeArgs, mostImportantArgNeg, normsupport,
		//		this.minimumOpinions(), 1);
		
	}

	//private String type = "minimum_support";
	private String type = "maximum_argument";
	//private String type = "counter_best";

	private String bestStatement = "";

	private Boolean forceNewArg = true;

	private double SUPPORT_THRESHOLD = 0.5;

	private Argument getArgFromStatement(String statement, Boolean pos) {
		if (pos) {
			for (Argument posArg : this.positiveArgs.getArguments()) {
				if (posArg.getStatement().equals(statement)) {
					return posArg;
				}
			}
		} else {
			for (Argument negArg : this.negativeArgs.getArguments()) {
				if (negArg.getStatement().equals(statement)) {
					return negArg;
				}
			}
		}
		return new Argument("", this.spec, new DefaultImportanceFunction(this.spec, 0.001));
	}

	private void tfg(PrintStream out, ArgumentSet positiveArgs2, HashMap bestPos, ArgumentSet negativeArgs2,
			HashMap bestNeg, Double normsupport, double minOpinions, int iteration) {

		// Condicions de sortida, printem el resultat
		if ((normsupport <= 0 && this.originalNormSupport >= 0)
				|| (normsupport >= 0 && this.originalNormSupport <= 0) || normsupport.isNaN()) {
			printStatusTFG(out, true, iteration);
		} else {

			if (normsupport <= 0 && this.originalNormSupport < 0) {

				if (this.type.equals("minimum_support")) {

					// En aquest cas ens trobem que la proposta ha estat rebutjada i hem d'afegir
					// arguments a favor per canviar el signe
					// Primer mirarem si tenim un argument rellevant a favor
					if (bestPos.containsKey("is_relevant") && !this.forceNewArg) {
						// En aquest cas, crearem copies d'aquest argument i anirem indicant-ho
						String statement = (String) bestPos.get("argument");
						Argument copy = new Argument("", this.spec, new DefaultImportanceFunction(this.spec, 0.001));

						for (Argument posArg : positiveArgs2.getArguments()) {
							if (posArg.getStatement().equals(statement)) {
								copy = posArg;
							}
						}

						copy.setStatement(copy.getStatement() + "_" + iteration);
						positiveArgs2.addArgument(copy);
						
						this.implementationInfo = "Afegim còpies del millor argument rellevant no alineat amb la proposta";

					} else {
						// Al no tenir cap argument a favor rellevant, haurem de crear-ne un
						Argument newArg = new Argument("newPosArg_" + iteration, this.spec, DEFAULT.importanceFunction(this.spec));

						// Afegirem les opinions necessaries per a que sigui considerat rellevant
						for (int i = 0; i < this.minimumOpinions(); i++) {
							newArg.addOpinion(1.);
						}

						// Afegim aquest nou argument a la llista
						positiveArgs2.addArgument(newArg);

						this.implementationInfo = "Es creen arguments mínimament rellevants amb el màxim suport";

						if(!this.forceNewArg){
							System.out.println("No s'ha trobat cap argument alfa-rellevant a favor de la proposta.");
							return;
						}
					}

				} else if (this.type.equals("maximum_argument")) {
					
					// En aquest cas afegirem un comentari positiu equivalent al millor comentari negatiu
					Argument newArg = new Argument("newPosArg_" + iteration, this.spec, DEFAULT.importanceFunction(this.spec));

					// Afegirem les opinions necessaries per a que sigui considerat rellevant
					for (int i = 0; i < (double) bestNeg.get("num_opinions"); i++) {
						newArg.addOpinion(1.);
					}

					// Afegim aquest nou argument a la llista
					positiveArgs2.addArgument(newArg);
				} else if (this.type.equals("counter_best")) {
					String statement;
					if (bestStatement.equals("")){
						statement = (String) bestNeg.get("argument");
						bestStatement = statement;
					} else {
						statement = bestStatement;
						if(this.getArgFromStatement(bestStatement, false).support() <= SUPPORT_THRESHOLD) {
							statement = (String) bestNeg.get("argument");
							bestStatement = statement;
						}
						
					}
										
					for (Argument negArg : negativeArgs2.getArguments()) {
						if (negArg.getStatement().equals(statement)) {
							negArg.addOpinion(-1);
						}
					}
					
					this.negativeArgs = negativeArgs2;
				}

				this.positiveArgs = positiveArgs2;

				// Reinicio les dades dels arguments rellevants per tornar a omplir les llistes
				positiveArgs2.argumentData = new ArrayList<>();
				negativeArgs2.argumentData = new ArrayList<>();

				// Aleshores tornem a cridar a la funció per calcular el nou suport a la norma
				printStatusTFG(out, false, iteration);

			} else {
				if (this.type.equals("minimum_support")) {
					// En aquest cas ens trobem que la proposta ha estat acceptada i hem d'afegir
					// arguments en contra per canviar el signe
					// Primer mirarem si tenim un argument rellevant en contra
					if (bestNeg.containsKey("is_relevant") && !this.forceNewArg) {
						// En aquest cas, crearem copies d'aquest argument i anirem indicant-ho
						String statement = (String) bestNeg.get("argument");
						Argument copy = new Argument("", this.spec, new DefaultImportanceFunction(this.spec, 0.001));

						for (Argument negArg : negativeArgs2.getArguments()) {
							if (negArg.getStatement().equals(statement)) {
								copy = negArg;
							}
						}

						copy.setStatement(copy.getStatement() + "_" + iteration);
						negativeArgs2.addArgument(copy);

						this.implementationInfo = "Afegim còpies del millor argument rellevant no alineat amb la proposta";

					} else {
						// Al no tenir cap argument en contra rellevant, haurem de crear-ne un
						Argument newArg = new Argument("newNegArg_" + iteration, this.spec, DEFAULT.importanceFunction(this.spec));

						// Afegirem les opinions necessaries per a que sigui considerat rellevant
						for (int i = 0; i < this.minimumOpinions(); i++) {
							newArg.addOpinion(1.);
						}

						// Afegim aquest nou argument a la llista
						negativeArgs2.addArgument(newArg);

						this.implementationInfo = "Es creen arguments mínimament rellevants amb el màxim suport";

						if(!this.forceNewArg){
							System.out.println("No s'ha trobat cap argument alfa-rellevant en contra de la proposta.");
							return;
						}
					}
				} else if (this.type.equals("maximum_argument")) {

					// En aquest cas afegirem un comentari positiu equivalent al millor comentari negatiu
					Argument newArg = new Argument("newNegArg_" + iteration, this.spec, DEFAULT.importanceFunction(this.spec));

					// Afegirem les opinions necessaries per a que sigui considerat rellevant
					for (int i = 0; i < (double) bestPos.get("num_opinions"); i++) {
						newArg.addOpinion(1.);
					}

					// Afegim aquest nou argument a la llista
					negativeArgs2.addArgument(newArg);
				} else if (this.type.equals("counter_best")) {
					String statement;
					if (bestStatement.equals("")){
						statement = (String) bestPos.get("argument");
						bestStatement = statement;
					} else {
						statement = bestStatement;
						if(this.getArgFromStatement(bestStatement, true).support() <= SUPPORT_THRESHOLD) {
							statement = (String) bestPos.get("argument");
							bestStatement = statement;
						}
						
					}
					
					for (Argument posArg : positiveArgs2.getArguments()) {
						if (posArg.getStatement().equals(statement)) {
							posArg.addOpinion(-1);
						}
					}

					this.positiveArgs = positiveArgs2;

				}

				this.negativeArgs = negativeArgs2;

				// Reinicio les dades dels arguments rellevants per tornar a omplir les llistes
				positiveArgs2.argumentData = new ArrayList<>();
				negativeArgs2.argumentData = new ArrayList<>();

				// Aleshores tornem a cridar a la funció per calcular el nou suport a la norma
				printStatusTFG(out, false, iteration);
			}
		}
	}

	public void printStatusTFG(PrintStream out, boolean printRes, int iteration) {
		Double possupport = this.positiveArgs.support(this.minimumOpinions());
		Double negsupport = this.negativeArgs.support(this.minimumOpinions());
		Double normsupport = this.support();

		if (printRes) {

			out.println("Norm:" + this.norm.getStatement());
			out.println("Spectrum:" + this.spec);
			out.println("Alpha: " + this.alpha);
			out.println(
					"\n   Results   \n-------------\n\nArguments in favor (argument, support, opinions recieved, alpha-relevance):");
			this.positiveArgs.printStatus(out, this.minimumOpinions());
			out.print("\nOverall support for the alpha-relevant arguments in favor: ");
			if (possupport.isNaN()) {
				out.println("Not defined");
			} else {
				out.format("%.4f\n", possupport);
			}
			out.println("\nArguments against (argument, support, opinions recieved, alpha-relevance):");
			this.negativeArgs.printStatus(out, this.minimumOpinions());
			out.print("\nOverall support for the alpha-relevant arguments against: ");
			if (negsupport.isNaN()) {
				out.println("Not defined");
			} else {
				out.format("%.4f\n", negsupport);
			}
			out.print("\nOverall support for the norm: ");
			if (normsupport.isNaN()) {
				out.println("Not defined");
			} else {
				out.format("%.4f\n", normsupport);
			}

		}

		System.out.println("\n\n\n\n");
		HashMap currArgMap;

		Double mostImportantArgValue = -99.;
		HashMap mostImportantArg = new HashMap<>();

		for (int i = 0; i < this.positiveArgs.argumentData.size(); i++) {
			currArgMap = this.positiveArgs.argumentData.get(i);
			if ((boolean) currArgMap.get("is_relevant")) {
				// printArgMap(currArgMap);
				if ((Double) currArgMap.get("weight") * (Double) currArgMap.get("support") > mostImportantArgValue) {
					mostImportantArgValue = (Double) currArgMap.get("weight") * (Double) currArgMap.get("support");
					mostImportantArg = currArgMap;
				}
			}
		}

		Double mostImportantArgValueNeg = -99.;
		HashMap mostImportantArgNeg = new HashMap<>();

		for (int i = 0; i < this.negativeArgs.argumentData.size(); i++) {
			currArgMap = this.negativeArgs.argumentData.get(i);
			if ((boolean) currArgMap.get("is_relevant")) {
				// printArgMap(currArgMap);
				if ((Double) currArgMap.get("weight") * (Double) currArgMap.get("support") > mostImportantArgValueNeg) {
					mostImportantArgValueNeg = (Double) currArgMap.get("weight") * (Double) currArgMap.get("support");
					mostImportantArgNeg = currArgMap;
				}
			}
		}

		if(mostImportantArg.containsKey("argument")){
			System.out.println("\n==================================");
			System.out.println("The most important + argument is: " + mostImportantArg.get("argument"));
			System.out.println("\tsupport = " + mostImportantArg.get("support"));
			System.out.println("\t# opinions = " + mostImportantArg.get("num_opinions"));
			System.out.println("\tImportance value = "
					+ (Double) mostImportantArg.get("weight") * (Double) mostImportantArg.get("support"));
			System.out.println("\n----------------------------------");
		}
		if(mostImportantArgNeg.containsKey("argument")){
			System.out.println("The most important - argument is: " + mostImportantArgNeg.get("argument"));
			System.out.println("\tsupport = " + mostImportantArgNeg.get("support"));
			System.out.println("\t# opinions = " + mostImportantArgNeg.get("num_opinions"));
			System.out.println("\tImportance value = "
					+ (Double) mostImportantArgNeg.get("weight") * (Double) mostImportantArgNeg.get("support"));
			System.out.println("\n==================================");
		}

		out.print("\nOverall support for the norm: ");
		if (normsupport.isNaN()) {
			out.println("Not defined");
		} else {
			out.format("%.4f\n", normsupport);
		}

		if (printRes) {
			System.out.println(this.implementationInfo);
			if(type == "counter_best"){
				System.out.println("Ha calgut afegir " + iteration + " opinions per modificar el resultat.");
			}else{
				System.out.println("Ha calgut afegir " + iteration + " arguments per modificar el resultat.");
			}
			System.out.println("- Arguments originals = " + this.originalArgsNum);
			System.out.println("Representa un " + iteration*100/this.originalArgsNum + "%");
			System.out.println("\tSuport original = " + this.originalNormSupport);
			System.out.println("\tSuport modificat = " + normsupport);
		} else {
			tfg(out, this.positiveArgs, mostImportantArg, this.negativeArgs, mostImportantArgNeg, normsupport, this.minimumOpinions(), iteration + 1);
		}
	}

	private void printArgMap(HashMap argMap){
		System.out.println(argMap.get("argument") + ":\n\t weight = " + argMap.get("weight"));
		System.out.println("\tsupport = " + argMap.get("support"));
		System.out.println("\t# opinions = " + argMap.get("num_opinions"));
	}
	
	/**
	 * Loads the norm argument map from a norm argument map file
	 * @param f The file to load (has to be a norm argument map file as defined in the project associated)
	 * @return The norm argument map loaded
	 * @throws FileNotFoundException If the file cannot be found to be read
	 */
	public static NormArgumentMap loadFile(File f) throws FileNotFoundException {
		NormArgumentMap nam = null;
		FileReader fr = new FileReader(f);
        Scanner scanner = new Scanner(fr);
		Scanner in = scanner.useDelimiter("\n");
		Spectrum spec = null;
		Norm n = null;
		String str;
		String[] list;
		Double alpha;
		if(in.hasNextLine()) {
			str = in.nextLine();
			list = str.split(",");
			if(list.length==4){
				n = new Norm(list[0]);
				if(list[1].isEmpty()){
					alpha = DEFAULT.alpha();
				} else{
					try{
						alpha = Double.parseDouble(list[1]);
					} catch(Exception e){
						System.err.println("WARNING: Unable to read alpha, default alpha was used instead");
						alpha = DEFAULT.alpha();
					}
					if((alpha > 1 || alpha < 0) && n!= null) {
						System.err.println("WARNING: Alpha must be in [0,1], default alpha was used instead");
						alpha = DEFAULT.alpha();
					}
				}
				try{
					spec = new Spectrum(Double.parseDouble(list[2]),Double.parseDouble(list[3]));
				} catch(Exception e) {
					System.err.println("WARNING: Unable to read spectrum");
					spec = null;
				}
				if(spec!=null){
					nam = new NormArgumentMap(n,alpha,spec);
				}
			}
		}
		if(nam!= null) {
			while(in.hasNextLine()){
				str = in.nextLine();
				list = str.split(",");
				Argument a = new Argument(list[1], nam.getSpec(), nam.getImportanceFunction());
				for(int i=2;i<list.length;i++) {
					try{
						a.addOpinion(Double.parseDouble(list[i]));
					} catch(Exception e){
						System.err.println("WARNING:Non valid opinion");
					}
				}
				nam.addArgument(a, Boolean.valueOf(list[0]));
			}
		} else{
			System.err.println("Empty or uncomplete file");
		}
        scanner.close();
		return nam;
	}
	
	

	public String getNorm() {
		return this.norm.getStatement();
	}

	public void setNorm(String s) {
		this.norm = new Norm(s);
	}

	public ArgumentSet getPositiveArgs() {
		return positiveArgs;
	}

	public ArgumentSet getNegativeArgs() {
		return negativeArgs;
	}
	
	public ImportanceFunction getImportanceFunction() {
		if(this.positiveArgs.getImportanceFunction()!=this.negativeArgs.getImportanceFunction()) {
			System.err.println("Importance function mismatch");
		}
		return this.positiveArgs.getImportanceFunction();
	}

	public Spectrum getSpec() {
		return spec;
	}
	
}
