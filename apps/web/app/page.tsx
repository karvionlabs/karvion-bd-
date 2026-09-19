"use client";

import React, { useState, useEffect } from "react";
import axios from "axios";
import { Mic, Send, Sparkles, Building2, Scale, GraduationCap, Leaf, AlertCircle, CheckCircle2 } from "lucide-react";
import { getFallbackResponse } from "./fallbackResponse";

export default function Home() {
  const [query, setQuery] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [consumerForm, setConsumerForm] = useState({ shop: "", product: "", issue: "" });
  const [copySuccess, setCopySuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const [selectedTab, setSelectedTab] = useState("Auto");

  const getDynamicComplaint = () => {
    return `বরাবর,
মহাপরিচালক
জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর
কারওয়ান বাজার, ঢাকা।

বিষয়: ${consumerForm.issue || 'অতিরিক্ত মূল্য আদায় / প্রতারণার অভিযোগ'}

জনাব,
আমি নিম্নস্বাক্ষরকারী, সম্প্রতি '${consumerForm.shop || '[দোকানের নাম]'}' থেকে '${consumerForm.product || '[পণ্যের নাম]'}' ক্রয় করতে গিয়ে প্রতারিত হয়েছি। বিস্তারিত তথ্য নিচে দেওয়া হলো:
- অভিযোগের বিবরণ: ${consumerForm.issue || 'অতিরিক্ত দাম / মেয়াদোত্তীর্ণ পণ্য'}
- প্রমাণ: সংযুক্ত

অতএব, বিনীত নিবেদন এই যে, উল্লেখিত ঘটনার যথাযথ আইনি ব্যবস্থা গ্রহণে মর্জি হয়।

বিনীত,
[আপনার নাম]
📞 ভোক্তা অধিকার হটলাইন: ১৬১২১`;
  };

  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      const textArea = document.createElement("textarea");
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      try {
        document.execCommand('copy');
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 2000);
      } catch (e) {}
      document.body.removeChild(textArea);
    }
  };
  
  const renderTextWithTable = (text: string) => {
    const lines = text.split('\n');
    const beforeTable: string[] = [];
    const tableLines: string[] = [];
    const afterTable: string[] = [];
    let inTable = false;
    let tableDone = false;

    lines.forEach(line => {
      if (line.trim().startsWith('|')) {
        inTable = true;
        if (!line.includes('---|')) {
          tableLines.push(line);
        }
      } else {
        if (inTable) {
          tableDone = true;
          inTable = false;
        }
        if (!tableDone) beforeTable.push(line);
        else afterTable.push(line);
      }
    });

    if (tableLines.length === 0) {
      return text;
    }

    const headers = tableLines[0].split('|').map(c => c.trim()).filter(c => c);
    const rows = tableLines.slice(1).map(line => line.split('|').map(c => c.trim()).filter(c => c));

    return (
      <div className="flex flex-col gap-4">
        <div className="whitespace-pre-wrap">{beforeTable.join('\n')}</div>
        <div className="w-full overflow-x-auto rounded-xl border border-gray-200 shadow-sm bg-white my-4">
          <table className="w-full text-left text-base text-gray-800">
            <thead className="bg-orange-50 text-orange-900 font-bold border-b border-orange-200 text-lg">
              <tr>
                {headers.map((h, i) => <th key={i} className="px-6 py-4">{h}</th>)}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {rows.map((row, i) => (
                <tr key={i} className="hover:bg-gray-50 transition-colors">
                  {row.map((cell, j) => (
                    <td key={j} className={`px-6 py-4 ${j > 0 ? 'font-bold text-gray-900 text-lg tracking-wide whitespace-nowrap' : 'font-semibold text-gray-800'}`}>
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="whitespace-pre-wrap">{afterTable.join('\n')}</div>
      </div>
    );
  };
  
  const suggestions = [
    "🎓 উচ্চশিক্ষার স্কলারশিপের সার্কুলার ও আবেদনের নিয়ম দেখাও",
    "⚖️ অতিরিক্ত দাম রাখায় ভোক্তা অধিকারে (DNCRP) অভিযোগ ড্রাফট করো",
    "🏛️ myGov পোর্টালের মাধ্যমে নাগরিক সেবা পাওয়ার ধাপগুলো বলো"
  ];

  const handleSpeech = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert("আপনার ব্রাউজার ভয়েস ইনপুট সাপোর্ট করে না। দয়া করে গুগল ক্রোম ব্যবহার করুন।");
      return;
    }
    const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'bn-BD';
    recognition.continuous = false;
    
    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setQuery(transcript);
    };
    
    recognition.start();
  };

  const handleSubmit = async (text: string, explicitTab?: string) => {
    if (!text.trim()) return;
    setIsLoading(true);
    setResponse(null);
    const currentTab = explicitTab || selectedTab;
    try {
      // Calling the FastAPI orchestrator endpoint
      const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
      const res = await axios.post(`${apiUrl}/api/v1/orchestrate`, {
        user_query: text,
        location: "Dhaka, Bangladesh",
        user_id: "demo-user-web",
        selected_agent: currentTab
      });
      setResponse(res.data);
    } catch (error) {
      console.warn("Backend unavailable. Using local fallback engine.", error);
      const fallback = getFallbackResponse(text, currentTab);
      setResponse(fallback);
    } finally {
      setIsLoading(false);
    }
  };

  const getAgentBadge = (agentName: string) => {
    switch (agentName) {
      case "Student Agent": return <div className="flex items-center gap-1 bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold"><GraduationCap size={16}/> Student Agent</div>;
      case "Consumer Agent": return <div className="flex items-center gap-1 bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-semibold"><Scale size={16}/> Consumer Agent</div>;
      case "Citizen Agent": return <div className="flex items-center gap-1 bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold"><Building2 size={16}/> Citizen Agent</div>;
      case "Farmer Agent": return <div className="flex items-center gap-1 bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-semibold"><Leaf size={16}/> Farmer Agent</div>;
      case "Market Agent": return <div className="flex items-center gap-1 bg-orange-100 text-orange-800 px-3 py-1 rounded-full text-sm font-semibold"><Building2 size={16}/> Market Agent</div>;
      case "Waste Agent": return <div className="flex items-center gap-1 bg-stone-100 text-stone-800 px-3 py-1 rounded-full text-sm font-semibold"><Sparkles size={16}/> Waste Agent</div>;
      default: return <div className="flex items-center gap-1 bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm font-semibold"><Sparkles size={16}/> Assistant</div>;
    }
  };

  const downloadPDF = async () => {
    if (!response) return;
    const contentToDownload = response.agent_name === "Consumer Agent" ? getDynamicComplaint() : response.next_action;
    if (!contentToDownload) return;
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
      const res = await axios.post(`${apiUrl}/api/v1/download-complaint-pdf`, 
        { content: contentToDownload }, 
        { responseType: 'blob' }
      );
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'DNCRP_Complaint.pdf');
      document.body.appendChild(link);
      link.click();
    } catch (error) {
      alert("PDF জেনারেট করতে সমস্যা হয়েছে।");
    }
  };

  return (
    <main className="max-w-4xl mx-auto p-6 md:p-12 flex flex-col items-center min-h-screen">
      {/* Branding Section */}
      <div className="text-center mb-10 w-full mt-10">
        <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-teal-600 to-blue-600 bg-clip-text text-transparent inline-block mb-3">
          KARVION BD
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 font-medium">AI Life & Service Automation</p>
        <p className="text-md text-gray-500 dark:text-gray-400 mt-2 italic">"বাংলায় বলুন, Karvion কাজের পথ তৈরি করবে।"</p>
      </div>

      {/* Category Tabs */}
      <div className="flex flex-wrap gap-2 justify-center w-full mb-6">
        {[
          { id: "Auto", label: "Auto Detection", icon: <Sparkles size={16}/> },
          { id: "Citizen Agent", label: "Citizen (৩৩৩)", icon: <Building2 size={16}/> },
          { id: "Student Agent", label: "Student (PMEAT)", icon: <GraduationCap size={16}/> },
          { id: "Market Agent", label: "Market (TCB)", icon: <Building2 size={16}/> },
          { id: "Consumer Agent", label: "Consumer (১৬১২১)", icon: <Scale size={16}/> },
          { id: "Farmer Agent", label: "Farmer (১৬১২৩)", icon: <Leaf size={16}/> },
          { id: "Waste Agent", label: "Waste Agent", icon: <Sparkles size={16}/> }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => {
              setSelectedTab(tab.id);
              if (tab.id !== "Auto") {
                // Auto trigger so the user doesn't have to type anything to see the agent's interface
                handleSubmit(`হ্যালো, আমাকে ${tab.id} এর সেবাগুলো সম্পর্কে জানান।`, tab.id);
              } else {
                setResponse(null);
              }
            }}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-colors shadow-sm border ${selectedTab === tab.id ? 'bg-teal-600 text-white border-teal-600' : 'bg-white text-gray-600 hover:bg-gray-50 border-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700'}`}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* Main Input Area */}
      <div className="w-full bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-2 border border-gray-100 dark:border-gray-700 relative flex items-center transition-all focus-within:ring-2 focus-within:ring-teal-500">
        <button 
          onClick={handleSpeech}
          className={`p-3 rounded-xl transition-colors ${isListening ? 'bg-red-100 text-red-600 animate-pulse' : 'text-gray-400 hover:text-teal-600 hover:bg-gray-50 dark:hover:bg-gray-700'}`}
          title="ভয়েস ইনপুট শুরু করুন"
        >
          <Mic size={24} />
        </button>
        <input 
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit(query)}
          placeholder="আপনার কি সাহায্য প্রয়োজন? (যেমন: স্কলারশিপ, অভিযোগ...)"
          className="flex-1 bg-transparent border-none outline-none px-4 py-3 text-lg text-gray-800 dark:text-white"
        />
        <button 
          onClick={() => handleSubmit(query)}
          disabled={isLoading || !query.trim()}
          className="p-3 bg-teal-600 text-white rounded-xl hover:bg-teal-700 transition-colors disabled:opacity-50 flex items-center justify-center"
        >
          {isLoading ? <span className="animate-spin h-6 w-6 border-2 border-white border-t-transparent rounded-full"></span> : <Send size={24} />}
        </button>
      </div>

      {/* Suggestion Chips */}
      <div className="mt-6 flex flex-wrap gap-2 justify-center w-full">
        {suggestions.map((sug, idx) => (
          <button 
            key={idx}
            onClick={() => { setQuery(sug); handleSubmit(sug); }}
            className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 px-4 py-2 rounded-full text-sm font-medium hover:border-teal-500 hover:text-teal-600 transition-all shadow-sm"
          >
            {sug}
          </button>
        ))}
      </div>

      {/* Interactive Output Card */}
      {response && (
        <div className="mt-12 w-full animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
            <div className="bg-gray-50 dark:bg-gray-900 px-6 py-4 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center">
              {getAgentBadge(response.agent_name)}
              <span className="text-xs text-gray-500 font-mono">Confidence: {(response.confidence_score * 100).toFixed(0)}%</span>
            </div>
            
            <div className="p-6 md:p-8">
              <div className="prose dark:prose-invert max-w-none whitespace-pre-wrap font-medium">
                {response.agent_name === "Consumer Agent" ? (
                  <div className="flex flex-col gap-4">
                    <h4 className="font-bold text-lg text-gray-800 dark:text-white">📝 ডাইনামিক অভিযোগপত্র তৈরি করুন</h4>
                    <p className="text-sm text-gray-500">আপনার তথ্য দিন, অভিযোগপত্র স্বয়ংক্রিয়ভাবে তৈরি হবে:</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <input 
                        type="text" 
                        placeholder="দোকান বা প্রতিষ্ঠানের নাম" 
                        value={consumerForm.shop}
                        onChange={(e) => setConsumerForm({...consumerForm, shop: e.target.value})}
                        className="border border-gray-300 p-2 rounded-lg"
                      />
                      <input 
                        type="text" 
                        placeholder="পণ্যের নাম" 
                        value={consumerForm.product}
                        onChange={(e) => setConsumerForm({...consumerForm, product: e.target.value})}
                        className="border border-gray-300 p-2 rounded-lg"
                      />
                      <input 
                        type="text" 
                        placeholder="অভিযোগের বিবরণ (যেমন: অতিরিক্ত দাম)" 
                        value={consumerForm.issue}
                        onChange={(e) => setConsumerForm({...consumerForm, issue: e.target.value})}
                        className="border border-gray-300 p-2 rounded-lg md:col-span-2"
                      />
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 font-mono text-sm whitespace-pre-wrap text-gray-700 dark:text-gray-300">
                      {getDynamicComplaint()}
                    </div>
                  </div>
                ) : (
                  renderTextWithTable(response.next_action)
                )}
              </div>
              
              {/* Extracted Entities */}
              {response.extracted_entities && response.extracted_entities.length > 0 && (
                <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-900 rounded-xl">
                  <h4 className="text-sm font-semibold text-gray-500 mb-2 uppercase tracking-wide">শনাক্তকৃত তথ্য</h4>
                  <div className="flex flex-wrap gap-2">
                    {response.extracted_entities.map((ent: any, idx: number) => (
                      <span key={idx} className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm">
                        <span className="text-teal-600 font-medium">{ent.entity_type}:</span> {ent.entity_value}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Official Action Portals (Mock Routing based on Agent) */}
              <div className="mt-8 flex gap-3 flex-wrap">
                {response.agent_name === "Consumer Agent" && (
                  <>
                    <button onClick={downloadPDF} className="inline-flex items-center gap-2 bg-gray-800 text-white px-5 py-2.5 rounded-xl font-semibold hover:bg-gray-700 transition-colors shadow-sm">
                      অভিযোগপত্র (PDF) ডাউনলোড করুন
                    </button>
                    <button 
                      onClick={() => handleCopy(getDynamicComplaint())} 
                      className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-5 py-2.5 rounded-xl font-semibold hover:bg-blue-100 transition-colors border border-blue-200 relative"
                    >
                      {copySuccess ? <CheckCircle2 size={18} /> : "কপি করুন"}
                      {copySuccess && <span className="absolute -top-8 bg-black text-white text-xs px-2 py-1 rounded">Copied!</span>}
                    </button>
                    <a 
                      href={`mailto:nccc@dncrp.gov.bd?subject=${encodeURIComponent(consumerForm.issue || 'অভিযোগ')}&body=${encodeURIComponent(getDynamicComplaint())}`}
                      className="inline-flex items-center gap-2 bg-indigo-50 text-indigo-700 px-5 py-2.5 rounded-xl font-semibold hover:bg-indigo-100 transition-colors border border-indigo-200"
                    >
                      ইমেইল পাঠান
                    </a>
                  </>
                )}
                {response.agent_name === "Citizen Agent" && (
                  <a href="https://www.mygov.bd/" target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 bg-green-50 text-green-700 px-5 py-2.5 rounded-xl font-semibold hover:bg-green-100 transition-colors border border-green-200">
                    <Building2 size={18} /> myGov পোর্টাল
                  </a>
                )}
                {response.agent_name === "Student Agent" && (
                  <>
                    <a href="https://pmeat.teletalk.com.bd/" target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-5 py-2.5 rounded-xl font-semibold hover:bg-blue-100 transition-colors border border-blue-200">
                      <GraduationCap size={18} /> PMEAT পোর্টাল (বাংলাদেশ)
                    </a>
                    <a href="https://www.studyinjapan.go.jp/en/" target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 bg-red-50 text-red-700 px-5 py-2.5 rounded-xl font-semibold hover:bg-red-100 transition-colors border border-red-200">
                      <GraduationCap size={18} /> MEXT স্কলারশিপ (জাপান)
                    </a>
                    <a href="https://erasmus-plus.ec.europa.eu/" target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 bg-emerald-50 text-emerald-700 px-5 py-2.5 rounded-xl font-semibold hover:bg-emerald-100 transition-colors border border-emerald-200">
                      <GraduationCap size={18} /> Erasmus (ইউরোপ)
                    </a>
                  </>
                )}
                {response.agent_name === "Farmer Agent" && (
                  <a href="https://moa.gov.bd/" target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 bg-yellow-50 text-yellow-700 px-5 py-2.5 rounded-xl font-semibold hover:bg-yellow-100 transition-colors border border-yellow-200">
                    <Leaf size={18} /> কৃষি মন্ত্রণালয় পোর্টাল
                  </a>
                )}
                {response.agent_name === "Waste Agent" && (
                  <div className="w-full bg-stone-50 border border-stone-200 rounded-xl p-6 mt-4">
                    <h4 className="text-lg font-bold text-stone-800 mb-4 flex items-center gap-2"><Sparkles /> বর্জ্য পিকআপ রিকোয়েস্ট ফর্ম</h4>
                    <form className="flex flex-col gap-3" onSubmit={(e) => { e.preventDefault(); alert("আপনার রিকোয়েস্ট সফলভাবে সাবমিট হয়েছে! প্রতিনিধি দ্রুত যোগাযোগ করবেন।"); }}>
                      <input type="text" placeholder="আপনার নাম" className="px-4 py-2 rounded-lg border border-gray-300" required />
                      <input type="tel" placeholder="মোবাইল নম্বর" className="px-4 py-2 rounded-lg border border-gray-300" required />
                      <select className="px-4 py-2 rounded-lg border border-gray-300" required>
                        <option value="">বর্জ্যের ধরন নির্বাচন করুন</option>
                        <option value="plastic">প্লাস্টিক বোতল ও স্ক্র্যাপ</option>
                        <option value="electronics">ইলেকট্রনিক্স (ই-বর্জ্য)</option>
                        <option value="paper">কাগজ / বই / কার্টন</option>
                        <option value="organic">পচনশীল বর্জ্য</option>
                      </select>
                      <textarea placeholder="বিস্তারিত ঠিকানা" className="px-4 py-2 rounded-lg border border-gray-300" rows={2} required></textarea>
                      <button type="submit" className="bg-stone-800 text-white font-bold py-3 rounded-lg hover:bg-stone-700 transition">রিকোয়েস্ট সাবমিট করুন</button>
                    </form>
                  </div>
                )}

              </div>
              
              {/* Fallback Hotlines */}
              <div className="mt-10 border-t border-gray-100 dark:border-gray-700 pt-6 flex flex-wrap gap-4 justify-between">
                <a href="tel:333" className="flex-1 min-w-[200px] text-center bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-4 hover:border-teal-500 transition-colors">
                  <div className="text-2xl font-bold text-teal-600">৩ ৩৩</div>
                  <div className="text-sm font-semibold text-gray-600 dark:text-gray-400">জাতীয় তথ্য বাতায়ন</div>
                </a>
                <a href="tel:16121" className="flex-1 min-w-[200px] text-center bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-4 hover:border-red-500 transition-colors">
                  <div className="text-2xl font-bold text-red-600">১৬১২১</div>
                  <div className="text-sm font-semibold text-gray-600 dark:text-gray-400">ভোক্তা অধিকার</div>
                </a>
                <a href="tel:16123" className="flex-1 min-w-[200px] text-center bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-4 hover:border-yellow-500 transition-colors">
                  <div className="text-2xl font-bold text-yellow-600">১৬১২৩</div>
                  <div className="text-sm font-semibold text-gray-600 dark:text-gray-400">কৃষি কল সেন্টার</div>
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
